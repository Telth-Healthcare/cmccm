import importlib
import inspect

from django.db import models, transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from core.permissions import RoleBasedPermission
from core.constants import Roles

from shg.services import SHGService

from .constants import PaymentClearance
from .models import Application
from .services import ApplicationService
from .serializers import ApplicationSerializer


class ApplicationConstantsAPI(APIView):
    permission_classes = []

    def get(self, request):
        CONSTANTS_MODULE = "applications.constants"
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


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    filter_backends = [OrderingFilter]
    ordering = ["-id"]
    serializer_class = ApplicationSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.FINANCIER, Roles.TRAINER],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "update": [Roles.SUPER_ADMIN],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # print(self.request.user.roles.all())    # Know who's accessing

        if user.has_role(Roles.SUPER_ADMIN):
            return qs
        elif user.has_role(Roles.ADMIN):
            return qs
        elif user.has_role(Roles.FINANCIER):
            """
            Fianacier should see applications assigned only to them
            """
            return qs.filter(assigned_financier=user).exclude(user__is_active=False)
        elif user.has_role(Roles.TRAINER):
            return qs.filter(assigned_trainer=user).exclude(payment_status=PaymentClearance.PENDING)

        return qs.filter(user=user)

    @transaction.atomic
    def perform_create(self, serializer):
        response = super().perform_create(serializer)
        shg = SHGService.get_shg(self.request.user)
        shg.is_submitted = True
        shg.save()
        ApplicationService.create_application(
            actor=self.request.user,
            application=serializer.instance,
        )
        return response
    
    def perform_update(self, serializer):
        response = super().perform_update(serializer)
        ApplicationService.update_application(
            actor=self.request.user,
            application=serializer.instance,
        )
        return response
    
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        ApplicationService.update_status(
            actor=self.request.user,
            application=self.get_object(),
            new_status=request.data.get("status"),
        )
        return response
