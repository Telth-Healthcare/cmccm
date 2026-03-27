from rest_framework import serializers

from django.db import transaction
from django.contrib.auth import get_user_model

from core.constants import Roles

User = get_user_model()

from .models import (
    Profile,
    Group,
    Course,
    Subject,
    SubjectMaterial,
    CourseEnrollment,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class SubjectMaterialSerializer(serializers.ModelSerializer):

    def validate(self, attrs: dict):
        if not attrs.get("url") and not attrs.get("file"):
            raise serializers.ValidationError({
                "detail": "'url' or 'file' must be provided."
            })
        return super().validate(attrs)

    class Meta:
        model = SubjectMaterial
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    materials = SubjectMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    aurthor = serializers.SerializerMethodField()

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
        exclude = ["permissions"]


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
                    dataset = []
                    for student in students:
                        dataset.append({
                            "user": student.pk,
                            "course": group.course.pk
                        })
                    serializer = CourseEnrollmentSerializer(
                        data=dataset,
                        many=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        return group

    def get_student_data(self, obj: Group):
        return [{"id": user.id, "name": user.get_full_name()} for user in obj.user_set.all()]
    
    def get_course_name(self, obj: Group):
        if obj.course:
            return obj.course.name
