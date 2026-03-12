from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import SHG, Document


class SHGSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    documents = serializers.SerializerMethodField()

    def get_documents(self, obj):
        shg = obj.user.shg
        if not shg:
            return None

        document = shg.documents.exists()
        if not document:
            return None
        
        payload = []
        for document in shg.documents.all():
            payload.append({
                "document_type": document.document_type,
                "file": document.file.url,
            })

        return payload

    class Meta:
        model = SHG
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


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

    def create(self, validated_data: dict):
        user = self.context["request"].user
        shg = SHG.objects.filter(user=user)
        if shg.exists():
            raise serializers.ValidationError("SHG already exists")
        return super().create(validated_data)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["id"]
