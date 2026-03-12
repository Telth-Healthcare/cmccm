from django.db import models


class Roles(models.TextChoices):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TRAINER = "trainer"
    FINANCIER = "financier"
    CM = "cm"
    CCM = "ccm"
