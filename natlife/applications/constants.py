from django.db import models


class ApplicationStatus(models.TextChoices):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ASSIGNED = "assigned"
    TRAINING = "training"
    PRODUCTION = "production"
    REJECTED = "rejected"


class PaymentClearance(models.TextChoices):
    PENDING = "pending"
    CLEARED = "cleared"
