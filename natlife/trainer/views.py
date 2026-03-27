import importlib
import inspect

from django.db import models

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.constants import Roles
from core.permissions import RoleBasedPermission

from .models import (
    Profile,
    Group,
    Course,
    Subject,
    CourseEnrollment,
    SubjectMaterial,
)
from .serializers import (
    ProfileSerializer,
    CourseSerializer,
    SubjectSerializer,
    SubjectMaterialSerializer,
    CourseEnrollmentSerializer,
    GroupEnrollmentSerializer,
    GroupSerializer,
)


class TrainerConstantsAPI(APIView):
    permission_classes = []

    def get(self, request):
        CONSTANTS_MODULE = "trainer.constants"
        module = importlib.import_module(CONSTANTS_MODULE)
        text_choices_classes = {
            name: cls
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, models.TextChoices) and cls.__module__ == CONSTANTS_MODULE
        }
        response_data = {}
        for name, cls in text_choices_classes.items():
            key = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
            response_data[key] = [{"value": c.value, "label": c.label} for c in cls]
        return Response(response_data)

class RoleFilteredQuerysetMixin:
    """
    Reusable mixin to filter queryset based on user role.
    """

    # Override this in child classes
    admin_filter = None
    trainer_filter = None
    partner_filter = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.has_role(Roles.SUPER_ADMIN):
            return qs

        if user.has_role(Roles.ADMIN):
            if not self.admin_filter:
                return qs.none()
            return qs.filter(**self.admin_filter(user))

        if user.has_role(Roles.TRAINER):
            if not self.trainer_filter:
                return qs.none()
            return qs.filter(**self.trainer_filter(user))
        
        if user.has_role(Roles.CM) or user.has_role(Roles.CCM):
            if not self.partner_filter:
                return qs.none()
            return qs.filter(**self.partner_filter(user))

        return qs.none()


class ProfileViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = Profile.objects.select_related("user", "user__region")
    serializer_class = ProfileSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN],
        "retrieve": [Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": [],
    }

    admin_filter = lambda self, user: {"user__region": user.region}
    trainer_filter = lambda self, user: {"user": user}


class CourseViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = Course.objects.select_related("created_by", "created_by__region")
    serializer_class = CourseSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER],
        "retrieve": [Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    admin_filter = lambda self, user: {"created_by__region": user.region}
    trainer_filter = lambda self, user: {"created_by": user}


class SubjectViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = Subject.objects.select_related(
        "course",
        "course__created_by",
        "course__created_by__region"
    )
    serializer_class = SubjectSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER],
        "retrieve": [Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    admin_filter = lambda self, user: {
        "course__created_by__region": user.region
    }
    trainer_filter = lambda self, user: {
        "course__created_by": user
    }


class SubjectMaterialViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = SubjectMaterial.objects.select_related(
        "subject",
        "subject__course",
        "subject__course__created_by",
        "subject__course__created_by__region"
    )
    serializer_class = SubjectMaterialSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER],
        "retrieve": [Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    admin_filter = lambda self, user: {
        "subject__course__created_by__region": user.region
    }
    trainer_filter = lambda self, user: {
        "subject__course__created_by": user
    }


class CourseEnrollmentViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.ADMIN, Roles.CM, Roles.CCM],
        "retrieve": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    partner_filter = lambda self, user: {"user": user}


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.TRAINER],
        "retrieve": [Roles.TRAINER],
        "create": [Roles.TRAINER],
        "update": [Roles.TRAINER],
        "partial_update": [Roles.TRAINER],
        "destroy": [Roles.TRAINER]
    }


class GroupEnrollmentView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "post": [Roles.TRAINER]
    }

    def post(self, request):
        serializer = GroupEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            results = serializer.save()
            return Response(results)
        return Response(serializer.errors, status=400)
