from datetime import timedelta
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


phone_validator = RegexValidator(
    regex=r'^\+[1-9]\d{11}$',
    message="Phone number must be starting with '+' and followed by valid country code and 10 digits."
)

class FileSizeValidator:
    def __init__(self, max_size_mb=5):
        self.max_size_mb = max_size_mb
        self.max_size = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(
                f"File too large. Maximum allowed size is {filesizeformat(self.max_size)}. "
                f"Current size is {filesizeformat(value.size)}."
            )

    def deconstruct(self):
        return (
            "core.validators.FileSizeValidator",  # full import path
            [self.max_size_mb],                   # args
            {},                                   # kwargs
        )

    def __eq__(self, other):
        return (
            isinstance(other, FileSizeValidator)
            and self.max_size_mb == other.max_size_mb
        )


def dob_validator(value):
    today = timezone.now().date()

    if value > today:
        raise ValidationError("Date of birth cannot be in the future.")

    min_dob = today - timedelta(days=55 * 365)
    max_dob = today - timedelta(days=18 * 365)

    if not (min_dob <= value <= max_dob):
        raise ValidationError("Age must be between 18 and 55.")
