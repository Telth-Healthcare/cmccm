from django.db import models
from django.conf import settings

from trainer.models import (
    MaterialCompletion,
    CourseEnrollment,
    CourseCompletion,
)

from .constants import (
    ApplicationStatus,
    PaymentType,
    PaymentMethod,
    PaymentClearance
)


AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL")


class Application(models.Model):

    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED,
    )

    payment_type = models.CharField(
        max_length=15,
        choices=PaymentType.choices,
        default=PaymentType.INSTALLMENTS,
    )

    payment_method = models.CharField(
        max_length=15,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE_PAYMENT,
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PaymentClearance.choices,
        default=PaymentClearance.PENDING,
    )

    assigned_financier = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_financier_applications",
    )

    assigned_trainer = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_trainer_applications",
    )

    reference_number = models.CharField(
        max_length=30,
        unique=True,
    )

    public_notes = models.TextField(blank=True)
    private_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference_number} - {self.status}"

    def get_enrollments(self):
        return CourseEnrollment.objects.filter(user=self.user)

    def get_subject_materials_completions(self):
        return MaterialCompletion.objects.filter(user=self.user)

    def get_course_completions(self):
        return CourseCompletion.objects.filter(user=self.user)

    def is_eligible_for_production(self):
        enrollments = self.get_enrollments()
        completed_courses = self.get_course_completions()

        if not enrollments.exists() or not completed_courses.exists():
            return False
        
        return enrollments.count() == completed_courses.count()

    class Meta:
        ordering = ["-created_at"]
