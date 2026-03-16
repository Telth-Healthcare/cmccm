from django.db import models

from core.validators import phone_validator


class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator], null=True, blank=True)
    email = models.EmailField()
    organization_type = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.email
