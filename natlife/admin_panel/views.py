from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q
from core.constants import Roles
from core.permissions import RoleBasedPermission
from accounts.models import User
from applications.models import Application

from .serializers import ApplicationSerializer


class DashboardAPIView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "get": [Roles.ADMIN, Roles.FINANCIER, Roles.TRAINER]
    }

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.all().exclude(
            roles__name__in=[Roles.SUPER_ADMIN]
        ).exclude(
            pk=user.pk
        )
        if user.has_role(Roles.SUPER_ADMIN):
            return qs
        elif user.has_role(Roles.ADMIN):
            return qs.filter(region=user.region)
        elif user.has_role(Roles.FINANCIER) or user.has_role(Roles.TRAINER):
            return qs.filter(
                Q(applications__assigned_financier=user) | 
                Q(applications__assigned_trainer=user),
            )
    
    def get_no_region_user_queryset(self):
        return self.get_queryset().filter(region=None)
    
    def get_application_queryset(self):
        user = self.request.user
        qs = Application.objects.all()

        if user.has_role(Roles.SUPER_ADMIN):
            return qs
        elif user.has_role(Roles.ADMIN):
            return qs.filter(user__region=user.region)


    def get(self, request):
        user_qs = self.get_queryset()
        application_qs = self.get_application_queryset()
    
        users_with_no_region = self.get_no_region_user_queryset().count()
        application_count = application_qs.count() if application_qs else 0

        applications = ApplicationSerializer(
            application_qs, many=True
        ).data

        data = {
            "total_users": user_qs.count(),
            "users_with_no_region": users_with_no_region,
            "total_applications": application_count,
            "applications": applications,
        }
        return Response(data)
