from django.db import models
from django.conf import settings


AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL")


class ActivityLog(models.Model):
    actor = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
    )

    action = models.CharField(max_length=255)

    object_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} on {self.object_type}:{self.object_id}"
