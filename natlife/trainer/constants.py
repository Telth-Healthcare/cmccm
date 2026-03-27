from django.db import models


class MaterialDocumentType(models.TextChoices):
    SYLLABUS = "syllabus"
    LECTURE_NOTES = "lecture_notes"
    ASSIGNMENT = "assignment"
    REFERENCE_MATERIAL = "reference_material"
    OTHER = "other"
