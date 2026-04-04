from rest_framework import serializers

from accounts.models import Pincode
from accounts.serializers import UserSerializer
from core.constants import Roles

from .models import SHG, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["id"]


class SHGSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = SHG
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def update(self, instance: SHG, validated_data: dict):
        pincode = validated_data.get("pin_code")
        if pincode:
            pincode_obj = Pincode.objects.filter(code=pincode)
            if pincode_obj.exists():
                region = pincode_obj.first().region
                instance.user.region = region
                instance.user.manager = region.admin
            instance.user.save()
        return super().update(instance, validated_data)


class CreateSHGSerializer(serializers.ModelSerializer):

    class Meta:
        model = SHG
        fields = [
            "id",
            "user",
            "dob",
            "language",
            "marital_status",
            "gender",
            "blood_group",
        ]
        read_only_fields = ["id"]
    
    def validate_user(self, user):
        if user.has_role(Roles.CM) or user.has_role(Roles.CCM):
            return user
        raise serializers.ValidationError(f"'{user.roles.first().name}' user cannot register as Partner.")

    def create(self, validated_data: dict):
        user = self.context["request"].user
        shg = SHG.objects.filter(user=user)
        if shg.exists():
            raise serializers.ValidationError("Partner already exists")
        return super().create(validated_data)
