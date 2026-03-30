import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.constants import Roles
from core.validators import phone_validator

from .managers import UserManager


class Role(models.Model):
    name = models.CharField(
        max_length=30,
        choices=Roles.choices,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)

    admin = models.OneToOneField(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_region"
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["id"]


class Pincode(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="pincodes"
    )
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.code} - {self.region}"

    class Meta:
        ordering = ["id"]


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=50, blank=True, default="")

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    phone_verified = models.BooleanField(default=False)

    roles = models.ManyToManyField(
        Role,
        related_name="users",
        blank=True
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates"
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users"
    )

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    # --------------------------------
    # Helpers
    # --------------------------------

    @property
    def role_names(self):
        return set(self.roles.values_list("name", flat=True))

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    def can_assign(self, role_name):
        if self.is_superuser:
            return True
        elif self.has_role(Roles.SUPER_ADMIN):
            return True
        elif self.has_role(Roles.ADMIN):
            return role_name not in [Roles.ADMIN, Roles.SUPER_ADMIN]
        return False

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.phone} - {self.get_full_name()}"

    class Meta:
        ordering = ["created_at"]
