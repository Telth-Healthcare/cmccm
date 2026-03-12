from django.db import models


class DocumentType(models.TextChoices):
    SYLLABUS = "SYLLABUS", "Syllabus"
    LECTURE_NOTES = "LECTURE_NOTES", "Lecture Notes"
    ASSIGNMENT = "ASSIGNMENT", "Assignment"
    REFERENCE_MATERIAL = "REFERENCE_MATERIAL", "Reference Material"
    OTHER = "OTHER", "Other"
