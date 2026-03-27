from django.db import models
from django.conf import settings
from django.core import validators

from core.validators import dob_validator, FileSizeValidator

from .constants import (
    Gender,
    MaritalStatus,
    BloodGroup,
    DocumentType,
    DocumentStatus,
    RegistrationStatus
)


AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class SHG(models.Model):
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shg"
    )
    dob = models.DateField(validators=[dob_validator])
    language = models.CharField(max_length=100)
    marital_status = models.CharField(
        max_length=50,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE
    )
    gender = models.CharField(
        max_length=50,
        choices=Gender.choices,
        default=Gender.MALE
    )
    blood_group = models.CharField(
        max_length=50,
        choices=BloodGroup.choices,
        default=BloodGroup.A_POSITIVE
    )

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100)
    village = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="IN")
    pin_code = models.CharField(
        max_length=6,
        validators=[
            validators.MinLengthValidator(6),
            validators.MaxLengthValidator(6)
        ]
    )

    registration_status = models.CharField(
        max_length=50,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.UNREGISTERED
    )

    is_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    shg = models.ForeignKey(
        SHG,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=100,
        choices=DocumentType.choices,
    )

    file = models.FileField(
        upload_to="documents/",
        max_length=500,
        validators=[FileSizeValidator(5)]
    )

    status = models.CharField(
        max_length=50,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.document_type} - {self.shg.user.get_full_name()}"


class BankDetails(models.Model):
    shg = models.OneToOneField(
        SHG,
        on_delete=models.CASCADE,
        related_name="bank_details"
    )
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(
        max_length=11,
        validators=[
            validators.MinLengthValidator(11),
            validators.MaxLengthValidator(11)
        ]
    )

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
