from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.constants import Roles
from core.permissions import RoleBasedPermission

from .models import (
    Profile,
    Group,
    Course,
    CourseCompletion,
    Subject,
    CourseEnrollment,
    SubjectMaterial,
    MaterialCompletion,
)
from .serializers import (
    ProfileSerializer,
    CourseSerializer,
    CourseCompletionSerializer,
    SubjectSerializer,
    SubjectMaterialSerializer,
    MaterialCompletionSerializer,
    CourseEnrollmentSerializer,
    GroupEnrollmentSerializer,
    GroupSerializer,
)


class RoleFilteredQuerysetMixin:
    """
    Filters querysets based on the requesting user's role.

    Usage: define any of the filter methods below in your ViewSet.
    Each method receives the requesting user and must return a dict
    of filter kwargs to apply to the queryset.

    Example:
        def admin_filter(self, user):
            return {"created_by__region": user.region}

        def trainer_filter(self, user):
            return {"created_by": user}
    """

    def admin_filter(self, user) -> dict | None:
        return None

    def trainer_filter(self, user) -> dict | None:
        return None

    def partner_filter(self, user) -> dict | None:
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        role_filter_map = [
            (Roles.SUPER_ADMIN, None),
            (Roles.ADMIN, self.admin_filter),
            (Roles.TRAINER, self.trainer_filter),
            (Roles.CM, self.partner_filter),
            (Roles.CCM, self.partner_filter),
        ]

        for role, filter_fn in role_filter_map:
            if user.has_role(role):
                if filter_fn is None:
                    return qs  # SUPER_ADMIN: unfiltered
                filters = filter_fn(user)
                return qs.filter(**filters).distinct() if filters else qs.none()

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

    def admin_filter(self, user):
        return {"user__region": user.region}
    
    def trainer_filter(self, user):
        return {"user": user}


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

    def admin_filter(self, user):
        return {"created_by__region": user.region}

    def trainer_filter(self, user):
        return {"created_by": user}


class CourseCompletionViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = CourseCompletion.objects.select_related("user", "course")
    serializer_class = CourseCompletionSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "retrieve": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "create": [Roles.CM, Roles.CCM],
        "update": [],
        "partial_update": [],
        "destroy": [],
    }

    def partner_filter(self, user):
        return {"user": user}


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

    def admin_filter(self, user):
        return {"course__created_by__region": user.region}

    def trainer_filter(self, user):
        return {"course__created_by": user}


class SubjectMaterialViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = SubjectMaterial.objects.select_related(
        "subject",
        "subject__course",
        "subject__course__created_by",
        "subject__course__created_by__region"
    ).distinct()
    serializer_class = SubjectMaterialSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "retrieve": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    def admin_filter(self, user):
        return {"subject__course__created_by__region": user.region}

    def trainer_filter(self, user):
        return {"subject__course__created_by": user}
    
    def partner_filter(self, user):
        return {"subject__course__enrollments__user": user}


class MaterialCompletionViewSet(ModelViewSet):
    queryset = MaterialCompletion.objects.all()
    serializer_class = MaterialCompletionSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.CM, Roles.CCM],
        "retrieve": [Roles.CM, Roles.CCM],
        "create": [Roles.CM, Roles.CCM],
        "destroy": [Roles.CM, Roles.CCM],
        "update": [],
        "partial_update": [],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Users only ever see their own completion records
        return qs.filter(
            user=self.request.user
        ).select_related("material")


class CourseEnrollmentViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "retrieve": [Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM],
        "create": [Roles.ADMIN, Roles.TRAINER],
        "update": [Roles.ADMIN, Roles.TRAINER],
        "partial_update": [Roles.ADMIN, Roles.TRAINER],
        "destroy": []
    }

    def trainer_filter(self, user):
        return {"user__applications__assigned_trainer": user}
    
    def partner_filter(self, user):
        return {"user": user}


class GroupViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
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

    def trainer_filter(self, user):
        return {"created_by": user}


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
