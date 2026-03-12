from rest_framework.viewsets import ModelViewSet

from core.constants import Roles
from core.permissions import RoleBasedPermission

from .models import (
    Profile,
    Course,
    CourseEnrollment,
    CourseMaterial,
)
from .serializers import (
    ProfileSerializer,
    CourseSerializer,
    CouserEnrollmentSerializer,
    CourseMaterialSerializer,
)


class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.has_role(Roles.SUPER_ADMIN):
            return qs
        elif user.has_role(Roles.ADMIN):
            return qs.filter(user__region=user.region)
        elif user.has_role(Roles.TRAINER):
            return qs.filter(user=user)
        else:
            return qs.none()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.TRAINER],
        "destroy": [Roles.SUPER_ADMIN]
    }


class CourseEnrollmentViewSet(ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CouserEnrollmentSerializer


class CourseMaterialViewSet(ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
