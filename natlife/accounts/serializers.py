from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from core.constants import Roles

from .services import AccountServices
from .models import Role, User, Region, Pincode, Invitation


INVITATION_TTL = getattr(settings, "INVITATION_TTL", 7)


class PincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pincode
        fields = "__all__"
        extra_kwargs = {
            "region": {"required": False}
        }


class RegionSerializer(serializers.ModelSerializer):
    pincodes = PincodeSerializer(many=True, read_only=False)

    class Meta:
        model = Region
        fields = "__all__"

    def create(self, validated_data: dict):
        pincodes: list[dict] = validated_data.pop("pincodes", [])
        region = super().create(validated_data)

        pincode_dataset = [
            Pincode(region=region, **pincode) for pincode in pincodes
        ]
        Pincode.objects.bulk_create(pincode_dataset)
        return region


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
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = Invitation
        exclude = ["token", "invited_by", "created_at"]
        read_only_fields = [
            "invited_by",
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
        region = attrs.get("region")
        roles = attrs.get("roles", [])

        role_names = {r.name for r in roles}

        self._validate_duplicates(email, phone, region)
        self._validate_permissions(inviter, role_names, attrs)

        return attrs

    def validate_region(self, value: Region):
        if value and value.admin:
            raise serializers.ValidationError("Region already has an admin.")
        return value

    def validate_manager(self, value: User):
        if value and not value.has_role(Roles.ADMIN):
            raise serializers.ValidationError(f"'{value.get_full_name()}' cannot be a manager.")
        return value

    # -------------------------
    # HELPERS
    # -------------------------

    def _validate_duplicates(self, email, phone, region):
        filters = Q()

        if email:
            filters |= Q(email=email)
        if phone:
            filters |= Q(phone=phone)

        qs = Invitation.objects.filter(filters)

        if qs.exists():
            if qs.filter(email=email, accepted=False).exists():
                raise serializers.ValidationError(
                    {"email": "Pending invitation exists for this email."}
                )

            if qs.filter(phone=phone, accepted=False).exists():
                raise serializers.ValidationError(
                    {"phone": "Pending invitation exists for this phone."}
                )

            if qs.filter(email=email).exists():
                raise serializers.ValidationError(
                    {"email": "Invitation already exists for this email."}
                )

            if qs.filter(phone=phone).exists():
                raise serializers.ValidationError(
                    {"phone": "Invitation already exists for this phone."}
                )

        if region and Invitation.objects.filter(region=region).exists():
            raise serializers.ValidationError(
                {"region": "Invitation already exists for this region."}
            )

    def _validate_permissions(self, inviter: User, role_names, attrs: dict):

        is_super_admin = inviter.has_role(Roles.SUPER_ADMIN)
        is_admin = inviter.has_role(Roles.ADMIN)

        # SUPER ADMIN
        if is_super_admin:

            if Roles.SUPER_ADMIN in role_names:
                raise serializers.ValidationError(
                    {"roles": "Cannot invite another super admin."}
                )

            if Roles.ADMIN in role_names:
                attrs["manager"] = None
                if not attrs.get("region"):
                    raise serializers.ValidationError(
                        {"region": "Admin must have a region."}
                    )
                return

            if role_names & {Roles.TRAINER, Roles.FINANCIER}:
                if not attrs.get("manager"):
                    raise serializers.ValidationError(
                        {"manager": "Trainer/Financier require a manager."}
                    )
                return

            if role_names & {Roles.CM, Roles.CCM}:
                raise serializers.ValidationError(
                    {"roles": "CM and CCM cannot be invited."}
                )

            return

        # ADMIN
        if is_admin:

            if Roles.ADMIN in role_names:
                raise serializers.ValidationError(
                    {"roles": "Admin cannot invite another admin."}
                )

            attrs["manager"] = inviter
            attrs["region"] = inviter.region
            return

        raise serializers.ValidationError("Not allowed to invite users.")

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, validated_data: dict):

        request = self.context["request"]
        inviter: User = request.user

        roles: list[Role] = validated_data.pop("roles")
        role_names = {r.name for r in roles}

        manager: User = validated_data.get("manager")

        if (
            role_names & {Roles.TRAINER, Roles.FINANCIER}
            and not validated_data.get("region")
            and manager
        ):
            validated_data["region"] = manager.region

        invitation = Invitation.objects.create(
            **validated_data,
            invited_by=inviter,
            expires_at=timezone.now() + INVITATION_TTL,
        )

        invitation.roles.set(roles)

        # Send email before saving is_sent
        raise NotImplementedError("TESTING")
        invitation.is_sent = AccountServices.send_invitation(request, invitation)
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
