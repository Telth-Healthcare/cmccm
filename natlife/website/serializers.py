from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "organization": {"required": True},
            "city": {"required": True},
            "phone": {"required": True},
            "organization_type": {"required": True},
        }


class WebinarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["email", "description"]
