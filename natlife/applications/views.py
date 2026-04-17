from django.db import transaction

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import RoleBasedPermission
from core.constants import Roles
from core.mixins import (
    RoleFilteredQuerysetMixin,
    RoleBasedLogFilterMixin,
)

from shg.services import SHGService

from .constants import PaymentClearance
from .models import Application
from .services import ApplicationService
from .serializers import ApplicationSerializer


class ApplicationViewSet(RoleFilteredQuerysetMixin, ModelViewSet):
    queryset = Application.objects.all()
    filter_backends = [OrderingFilter]
    ordering = ["-id"]
    serializer_class = ApplicationSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.ADMIN, Roles.FINANCIER, Roles.TRAINER],
        "retrieve": [Roles.ADMIN, Roles.FINANCIER, Roles.CM, Roles.CCM],
        "create": [Roles.ADMIN, Roles.CM, Roles.CCM],
        "update": [Roles.ADMIN],
        "partial_update": [Roles.ADMIN, Roles.FINANCIER, Roles.TRAINER],
        "destroy": [],
    }

    def admin_filter(self, user):
        return {
            "user__region": user.region,
            "user__is_active": True,
        }

    def financier_filter(self, user):
        return {
            "assigned_financier": user,
            "user__is_active": True,
        }

    def trainer_filter(self, user):
        return {
            "assigned_trainer": user,
            "payment_status": PaymentClearance.PENDING,
        }
    
    def partner_filter(self, user):
        return {"user": user}

    @transaction.atomic
    def perform_create(self, serializer):
        response = super().perform_create(serializer)
        shg = SHGService.get_shg(serializer.instance.user)
        shg.is_submitted = True
        shg.save()
        ApplicationService.create_application(
            actor=self.request.user,
            application=serializer.instance,
        )
        return response

    def partial_update(self, request, *args, **kwargs):
        ApplicationService.update_status(
            actor=self.request.user,
            application=self.get_object(),
            new_status=request.data.get("status"),
        )
        return super().partial_update(request, *args, **kwargs)


class ApplicationActivityLogAPIView(
    RoleBasedLogFilterMixin,
    ListModelMixin,
    GenericViewSet
):
    queryset = ApplicationService.get_application_logs()
    model = Application
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [
            Roles.ADMIN, Roles.FINANCIER, Roles.TRAINER,
            Roles.CM, Roles.CCM
        ]
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"object_id": ["exact"]}
