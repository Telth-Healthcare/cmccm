from django.db import models


class Gender(models.TextChoices):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatus(models.TextChoices):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


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
    TENTH_CERTIFICATE = "tenth_certificate"
    TWELFTH_CERTIFICATE = "twelfth_certificate"
    DIPLOMA = "diploma"
    BACHELOR_DEGREE = "bachelor_certificate"
    MASTERS_DEGREE = "master_certificate"
    PHD_DEGREE = "phd_certificate"
    EXPERIENCE_CERTIFICATE = "experience_certificate"
    BANK_DOC = "bank_doc"
    OTHER = "other"


class DocumentStatus(models.TextChoices):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REUPLOADED = "reuploaded"


class RegistrationStatus(models.TextChoices):
    REGISTERED = "registered"
    UNREGISTERED = "unregistered"
    IN_PROCESS = "in_process"
