from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from core.constants import Roles

from .models import Application
from .services import ApplicationService
from .constants import ApplicationStatus

ALLOWED_TRANSITIONS = {
    ApplicationStatus.SUBMITTED: [
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.REJECTED,
    ],
    ApplicationStatus.UNDER_REVIEW: [
        ApplicationStatus.ASSIGNED,
        ApplicationStatus.REJECTED,
    ],
    ApplicationStatus.ASSIGNED: [
        ApplicationStatus.TRAINING,
    ],
    ApplicationStatus.TRAINING: [
        ApplicationStatus.PRODUCTION,
    ],
    ApplicationStatus.PRODUCTION: [],
    ApplicationStatus.REJECTED: [],
}


class ApplicationSerializer(ModelSerializer):
    user_details = SerializerMethodField()
    financier_details = SerializerMethodField()
    trainer_details = SerializerMethodField()
    shg = SerializerMethodField()
    documents = SerializerMethodField()

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = [
            "reference_number",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs: dict):
        user = self.context.get("request").user
        if user.has_role(Roles.TRAINER):
            attrs = {"status": attrs.get("status", ApplicationStatus.TRAINING)}
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["reference_number"] = ApplicationService.generate_reference_number()
        return super().create(validated_data)

    def validate_status(self, value):
        if not self.instance:
            return value

        instance: Application = self.instance
        current_status = instance.status
        if current_status == value:
            return value

        allowed = ALLOWED_TRANSITIONS.get(current_status, [])

        if value not in allowed:
            raise ValidationError(f"Cannot transition from {current_status} to {value}")

        is_eligible = instance.is_eligible_for_production()
        if value == ApplicationStatus.PRODUCTION and not is_eligible:
            raise ValidationError({
                "status": "This application is not eligible for production"
            })

        return value

    def get_user_details(self, obj):
        return obj.user.get_full_name()

    def get_financier_details(self, obj):
        return obj.assigned_financier.get_full_name() if obj.assigned_financier else None

    def get_trainer_details(self, obj):
        return obj.assigned_trainer.get_full_name() if obj.assigned_trainer else None

    def get_shg(self, obj):
        return obj.user.shg.id if obj.user.shg else None

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
