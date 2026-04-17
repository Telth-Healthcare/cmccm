from rest_framework import serializers

from .models import ActivityLog


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    to = serializers.EmailField()
    html_content = serializers.CharField()
    text_content = serializers.CharField()


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
