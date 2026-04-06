from django.db import models
from django.conf import settings

from django.contrib.auth.models import Group as BaseGroup

from core.validators import FileSizeValidator

from .constants import MaterialDocumentType


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
    
    class Meta:
        ordering = ["-created_at"]


class Group(BaseGroup):
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="groups",
        null=True,
        blank=True
    )
    
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    img = models.ImageField(
        upload_to="course_images/",
        max_length=500,
        validators=[FileSizeValidator(3)],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses_created",
    )

    class Meta:
        ordering = ["-created_at"]


class Subject(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    img = models.ImageField(
        upload_to="subject_images/",
        max_length=50,
        validators=[FileSizeValidator(3)],
        null=True,
        blank=True
    )


    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name}"


class SubjectMaterial(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=MaterialDocumentType.choices)
    url = models.URLField(null=True, blank=True)
    file = models.FileField(
        upload_to="course_materials/",
        max_length=500,
        validators=[FileSizeValidator(30)],
        null=True,
        blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title}"


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

    def is_eligible_for_completion(self):
        materials_qs = SubjectMaterial.objects.filter(subject__course=self.course)
        if not materials_qs.exists():
            return False
        return not materials_qs.exclude(
            completions__user=self.user
        ).exists()

    def __str__(self):
        return f"{self.user.get_full_name()} enrolled in {self.course.name}"

    class Meta:
        ordering = ["-enrollment_date"]
        unique_together = ("user", "course")


class CourseCompletion(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_completions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        unique_together = ("user", "course")
    
    def __str__(self):
        return f"{self.user.get_full_name()} completed {self.course.name}"


class MaterialCompletion(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="material_completions",
    )
    material = models.ForeignKey(
        SubjectMaterial,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "material")  # prevents duplicate completion records

    def __str__(self):
        return f"{self.user.get_full_name()} completed {self.material.title}"
