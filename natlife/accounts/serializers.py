from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.db.models import Q, Exists, OuterRef

from allauth.account.models import EmailAddress

from core.constants import Roles

from .models import Role, User, Region, Pincode


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
    invite_accepted = serializers.SerializerMethodField(read_only=True)


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
    
    def get_invite_accepted(self, obj: User):
        return obj.emailaddress_set.filter(verified=True).exists()

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

    # Forbidden roles for invite (used in both validate_roles and _validate_permissions)
    UNINVITABLE_ROLES: frozenset[str] = frozenset({Roles.SUPER_ADMIN, Roles.CM, Roles.CCM})
    MANAGER_REQUIRED_ROLES: frozenset[str] = frozenset({Roles.TRAINER, Roles.FINANCIER})

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "roles",
            "region",
            "manager",
            "region_name",
        ]
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
            "phone": {"required": True, "allow_blank": False},
            "roles": {"required": True},
        }

    # -------------------------
    # FIELD-LEVEL VALIDATION
    # -------------------------

    def validate_email(self, value: str) -> str:
        return value.lower() if value else value

    def validate_region(self, value: Region) -> Region:
        if value and value.admin:
            raise serializers.ValidationError("Region already has an admin.")
        return value

    def validate_manager(self, value: User) -> User:
        if value and not value.has_role(Roles.ADMIN):
            raise serializers.ValidationError(
                f"'{value.get_full_name()}' cannot be a manager."
            )
        return value

    def validate_roles(self, value: list[Role]) -> list[Role]:
        forbidden = {r.name for r in value} & self.UNINVITABLE_ROLES
        if forbidden:
            raise serializers.ValidationError(
                f"Cannot invite role(s): {', '.join(forbidden)}."
            )
        return value

    # -------------------------
    # OBJECT-LEVEL VALIDATION
    # -------------------------

    def validate(self, attrs: dict) -> dict:
        inviter: User = self.context["request"].user
        role_names: frozenset[str] = frozenset(r.name for r in attrs.get("roles", []))

        self._validate_duplicates(
            email=attrs.get("email"),
            phone=attrs.get("phone"),
        )
        self._validate_permissions(inviter, role_names, attrs)

        return attrs

    # -------------------------
    # HELPERS
    # -------------------------

    @staticmethod
    def _raise(field: str, message: str) -> None:
        """Shorthand for raising a field-level ValidationError."""
        raise serializers.ValidationError({field: message})

    def _validate_duplicates(
        self,
        email: str | None,
        phone: str | None,
    ) -> None:
        """
        Single DB round-trip to check email/phone uniqueness,
        then one extra query only if region is provided.
        """
        filters = Q()
        if email:
            filters |= Q(email=email)
        if phone:
            filters |= Q(phone=phone)

        if filters:
            # Annotate verified status in one query instead of four
            conflicts = (
                User.objects.filter(filters)
                .annotate(is_verified=Exists(
                    EmailAddress.objects.filter(
                        user=OuterRef("pk"),
                        verified=True,
                    )
                ))
                .values("email", "phone", "is_verified")
            )

            for row in conflicts:
                verified: bool = row["is_verified"]
                status: str = "already exists" if verified else "pending invitation exists"

                if email and row["email"] == email:
                    self._raise("email", f"An invitation {status} for this email.")
                if phone and row["phone"] == phone:
                    self._raise("phone", f"An invitation {status} for this phone.")

    def _validate_permissions(
        self,
        inviter: User,
        role_names: frozenset[str],
        attrs: dict,
    ) -> None:
        """Mutates attrs in-place to enforce role/region/manager rules per inviter."""

        # --- SUPER ADMIN ---
        if inviter.has_role(Roles.SUPER_ADMIN):
            if Roles.SUPER_ADMIN in role_names:
                self._raise("roles", "Cannot invite another super admin.")

            if Roles.ADMIN in role_names:
                attrs["manager"] = None
                if not attrs.get("region"):
                    self._raise("region", "Admin must have a region.")
                return

            if role_names & self.MANAGER_REQUIRED_ROLES:
                if not attrs.get("manager"):
                    self._raise("manager", "Trainer/Financier require a manager.")
                return

            # CM / CCM already blocked in validate_roles; nothing else to check
            return

        # --- ADMIN ---
        if inviter.has_role(Roles.ADMIN):
            if Roles.ADMIN in role_names:
                self._raise("roles", "Admin cannot invite another admin.")

            attrs["manager"] = inviter
            attrs["region"] = inviter.region
            return

        raise serializers.ValidationError("Not allowed to invite users.")

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, validated_data: dict) -> User:
        roles: list[Role] = validated_data.pop("roles")
        role_names: frozenset[str] = frozenset(r.name for r in roles)

        # Inherit manager's region for Trainer/Financier in one conditional
        manager: User = validated_data.get("manager")
        if manager and role_names & self.MANAGER_REQUIRED_ROLES:
            validated_data["region"] = manager.region

        user: User = super().create(validated_data)
        user.roles.set(roles)

        # get_or_create avoids a double-insert race; send confirmation in one step
        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={"verified": False},
        )
        email_address.send_confirmation()

        return user


class AcceptInviteSerializer(serializers.Serializer):

    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

class FirebaseLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    phone_verified = serializers.CharField(required=True)
