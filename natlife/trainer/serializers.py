from rest_framework import serializers

from django.db import transaction
from django.contrib.auth import get_user_model

from core.constants import Roles

User = get_user_model()

from .models import (
    Profile,
    Group,
    Course,
    CourseCompletion,
    Subject,
    SubjectMaterial,
    MaterialCompletion,
    CourseEnrollment,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class IsCompletedMixin:
    """
    Adds a read-only `is_completed` field that reflects the requesting
    user's completion status via a `completions` reverse relation.
    """
    def get_is_completed(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        return obj.completions.filter(user=request.user).exists()


class SubjectMaterialSerializer(serializers.ModelSerializer, IsCompletedMixin):
    is_completed = serializers.SerializerMethodField()

    def validate(self, attrs: dict):
        url = attrs.get("url") or getattr(self.instance, "url", None)
        file = attrs.get("file") or getattr(self.instance, "file", None)

        if not url and not file:
            raise serializers.ValidationError({
                "detail": "'url' or 'file' must be provided."
            })
        return attrs

    class Meta:
        model = SubjectMaterial
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    materials = SubjectMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer, IsCompletedMixin):
    subjects = SubjectSerializer(many=True, read_only=True)
    aurthor = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    def get_aurthor(self, obj: Course):
        return obj.created_by.get_full_name()

    class Meta:
        model = Course
        fields = "__all__"
        extra_kwargs = {
            "created_by": {
                "required": False,
                "allow_null": False,
                "error_messages": {
                    "required": "This field is required.",
                    "allow_null": "This field cannot be null.",
                }
            }
        }

    def validate(self, attrs: dict):
        user = self.context["request"].user

        if user.has_role(Roles.TRAINER):
            attrs["created_by"] = user
        else:
            if not attrs.get("created_by"):
                raise serializers.ValidationError({
                    "created_by": ["This field is required."]
                })

        return attrs


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    course_details = CourseSerializer(source="course", read_only=True)
    application_id = serializers.SerializerMethodField()

    class Meta:
        model = CourseEnrollment
        fields = "__all__"
        extra_kwargs = {
            "course": {"write_only": True}
        }


    def validate_user(self, value):
        if not (value.has_role(Roles.CM) or value.has_role(Roles.CCM)):
            raise serializers.ValidationError([
                f"{value.get_full_name()} is not eligible for enrolling."
            ])
        return value

    def get_user_name(self, obj: CourseEnrollment):
        return obj.user.get_full_name()

    def get_application_id(self, obj: CourseEnrollment):
        application = obj.user.applications
        return application.id if application else None


class CourseCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletion
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}  # always set from request, never from client
        }

    def validate(self, attrs: dict):
        user = self.context["request"].user
        course = attrs["course"]

        if CourseCompletion.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError({"detail": "Already completed."})

        enrollment = CourseEnrollment.objects.filter(user=user, course=course).first()
        if not enrollment or not enrollment.is_eligible_for_completion():
            raise serializers.ValidationError({"detail": "Not eligible for completion."})

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class MaterialCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCompletion
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True}  # always set from request, never from client
        }

    def validate(self, attrs: dict):
        user = self.context["request"].user
        material = attrs.get("material")

        if MaterialCompletion.objects.filter(user=user, material=material).exists():
            raise serializers.ValidationError({
                "detail": "This material is already marked as completed."
            })
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class GroupSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    student_data = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        exclude = ["permissions", "created_by"]


    def validate_students(self, value):
        if value:
            for user in value:
                if not (user.has_role(Roles.CM) or user.has_role(Roles.CCM)):
                    raise serializers.ValidationError({
                        "students": [
                            f"'{user.get_full_name()}' is not eligible to be a "
                            "student therefore cannot be added to the group."
                        ]
                    })
        return value


    def create(self, validated_data: dict):
        students = validated_data.pop("students", [])
        validated_data["created_by"] = self.context["request"].user
        group: Group = super().create(validated_data)
        group.user_set.add(*students)
        return group


    def update(self, instance: Group, validated_data: dict):
        students = validated_data.pop("students", [])
        group: Group = super().update(instance, validated_data)

        if students:
            with transaction.atomic():
                group.user_set.set(students)
                if group.course:
                    existing_ids = set(
                        CourseEnrollment.objects.filter(course=group.course)
                        .values_list("user_id", flat=True)
                    )
                    new_students = [s for s in students if s.pk not in existing_ids]
                    enrollments = [
                        CourseEnrollment(user=s, course=group.course)
                        for s in new_students
                    ]
                    CourseEnrollment.objects.bulk_create(enrollments)
        return group

    def get_student_data(self, obj: Group):
        return [{"id": user.id, "name": user.get_full_name()} for user in obj.user_set.all()]
    
    def get_course_name(self, obj: Group):
        if obj.course:
            return obj.course.name


class GroupEnrollmentSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=True,
        write_only=True
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        required=True,
        write_only=True
    )

    @transaction.atomic
    def create(self, validated_data: dict):
        group: Group = validated_data.pop("group", None)
        course: Course = validated_data["course"]

        group.course = course

        users = group.user_set.all()

        results = {
            "created": [],
            "failed": []
        }

        # Get already enrolled users
        existing_user_ids = set(
            CourseEnrollment.objects.filter(course=course)
            .values_list("user_id", flat=True)
        )

        for u in users:
            if u.pk in existing_user_ids:
                results["failed"].append({
                    "user": u.pk,
                    "error": "Already enrolled"
                })
                continue

            serializer = CourseEnrollmentSerializer(
                data={"user": u.pk, "course": course.pk}
            )

            if serializer.is_valid():
                enrollment = serializer.save()
                results["created"].append({
                    "user": u.pk,
                    "enrollment_id": enrollment.id
                })
            else:
                results["failed"].append({
                    "user": u.pk,
                    "error": serializer.errors
                })

        group.save()
        return results
