from django.db import models


class ApplicationStatus(models.TextChoices):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ASSIGNED = "assigned"
    TRAINING = "training"
    PRODUCTION = "production"
    ACTION_REQUIRED = "action_required"
    REJECTED = "rejected"


class PaymentType(models.TextChoices):
    INSTALLMENTS = "installments"
    FULL_PAYMENT = "full_payment"


class PaymentMethod(models.TextChoices):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    ONLINE_PAYMENT = "online_payment"
    MOBILE_MONEY = "mobile_money"
    CARD = "card"


class PaymentClearance(models.TextChoices):
    PENDING = "pending"
    CLEARED = "cleared"
