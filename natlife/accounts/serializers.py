from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from core.constants import Roles

from .services import AccountServices
from .models import Role, User, Region, Invitation


INVITATION_TTL = getattr(settings, "INVITATION_TTL", 7)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    roles = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Role.objects.all(),
        required=True
    )
    has_password = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = User
        exclude = [
            "password",
            "groups",
            "user_permissions",
            "is_superuser",
            "is_staff",
            "last_login",
        ]
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
            "region": {"required": True},
        }

    def create(self, validated_data: dict):
        try:
            validated_data["created_by"] = self.context["request"].user
        except KeyError:
            pass
        finally:
            return super().create(validated_data)

    def validate_roles(self, value: list[Role]):
        user: User = self.context["request"].user
        for role in value:
            if not user.can_assign(role.name):
                raise serializers.ValidationError(f"You cannot assign {role.name} role.")
        return value
    
    def validate_email(self, value: str):
        if value:
            return value.lower()
        return value

    def get_has_password(self, obj: User):
        return True if obj.password else False


class SendInviteSerializer(serializers.ModelSerializer):

    roles = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Role.objects.all(),
    )

    class Meta:
        model = Invitation
        exclude = [
            "token",
            "region",
            "manager",
            "invited_by",
            "created_at",
        ]
        read_only_fields = [
            "invited_by"
            "is_sent",
            "accepted",
            "expires_at",
            "created_at",
        ]

    # -------------------------
    # VALIDATION
    # -------------------------

    def validate(self, attrs: dict):

        request = self.context["request"]
        inviter: User = request.user

        email = attrs.get("email")
        phone = attrs.get("phone")
        roles: list[Role] = attrs.get("roles", [])

        role_names = {r.name for r in roles}

        self._validate_duplicate_invite(email, phone)
        self._validate_inviter_permissions(inviter, role_names, attrs)

        return attrs


    def _validate_duplicate_invite(self, email: str, phone: str):

        qs = Invitation.objects.filter(Q(email=email) | Q(phone=phone))

        if not qs.exists():
            return

        if qs.filter(email=email, accepted=False).exists():
            raise serializers.ValidationError(
                {"email": "A pending invitation already exists for this email."}
            )

        if qs.filter(phone=phone).exists():
            raise serializers.ValidationError(
                {"phone": "An invitation already exists for this phone number."}
            )

        raise serializers.ValidationError(
            {"email": "An invitation already exists for this email."}
        )


    def _validate_inviter_permissions(self, inviter: User, role_names: set, attrs: dict):

        # SUPER ADMIN
        if inviter.has_role(Roles.SUPER_ADMIN):

            if Roles.ADMIN in role_names:
                attrs["manager"] = None
                return

            if role_names.intersection({Roles.TRAINER, Roles.FINANCIER}):
                if not attrs.get("manager"):
                    raise serializers.ValidationError(
                        {"manager": "Trainer/Financier must have a manager."}
                    )
                return
            
            if role_names.intersection({Roles.CM, Roles.CCM}):
                return

        # ADMIN
        if inviter.has_role(Roles.ADMIN):

            if Roles.ADMIN in role_names:
                raise serializers.ValidationError(
                    {"roles": "Admin cannot invite another admin."}
                )

            attrs["manager"] = inviter
            attrs["region"] = inviter.region
            return

        raise serializers.ValidationError(
            "You are not allowed to invite users."
        )


    # -------------------------
    # CREATE
    # -------------------------

    def create(self, validated_data: dict):

        request = self.context["request"]
        inviter: User = request.user

        roles: list[Role] = validated_data.pop("roles")

        role_names = {r.name for r in roles}

        is_staff_role = bool(
            role_names.intersection({Roles.TRAINER, Roles.FINANCIER})
        )

        manager = validated_data.get("manager")

        if is_staff_role and not validated_data.get("region") and manager:
            validated_data["region"] = manager.region

        invitation = Invitation.objects.create(
            **validated_data,
            invited_by=inviter,
            expires_at=timezone.now() + INVITATION_TTL,
        )

        invitation.roles.set(roles)

        is_sent = AccountServices.send_invitation(request, invitation)
        invitation.is_sent = is_sent
        invitation.save(update_fields=["is_sent"])

        return invitation


class AcceptInviteSerializer(serializers.Serializer):

    token = serializers.UUIDField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )


class FirebaseLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    phone_verified = serializers.CharField(required=True)
