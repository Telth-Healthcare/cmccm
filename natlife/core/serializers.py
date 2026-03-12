from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    to = serializers.EmailField()
    html_content = serializers.CharField()
    text_content = serializers.CharField()
