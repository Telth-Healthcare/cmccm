from django.db import models


class Gender(models.TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class MaritalStatus(models.TextChoices):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"


class BloodGroup(models.TextChoices):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class DocumentType(models.TextChoices):
    AADHAR_CARD_FRONT = "aadhar_front"
    AADHAR_CARD_BACK = "aadhar_back"
    PAN_CARD = "pan"
    BACHELOR_DEGREE = "bachelor_certificate"
    MASTERS_DEGREE = "master_certificate"
    PHD_DEGREE = "phd_certificate"
    EXPERIENCE_CERTIFICATE = "experience_certificate"
    BANK_DOC = "bank_doc"
    OTHER = "other"


class RegistrationStatus(models.TextChoices):
    REGISTERED = "Registered"
    UNREGISTERED = "Unregistered"
    IN_PROCESS = "In Process"
