from django.db import models
from django.conf import settings

from core.validators import FileSizeValidator

from .constants import DocumentType


AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL")


class Profile(models.Model):
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class CourseEnrollment(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")


class CourseMaterial(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="course_materials",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=DocumentType.choices)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to="course_materials/", validators=[FileSizeValidator(3)])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "course")
