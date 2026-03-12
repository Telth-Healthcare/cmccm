import importlib
import inspect

from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import RoleBasedPermission
from core.constants import Roles

from .models import SHG, Document
from .serializers import (
    CreateSHGSerializer,
    SHGSerializer,
    DocumentSerializer,
)


CONSTANTS_MODULE = "shg.constants"

class SHGConstantMetaAPI(APIView):
    permission_classes = []

    def get(self, request):
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


class SHGViewSet(ModelViewSet):
    queryset = SHG.objects.all()
    serializer_class = SHGSerializer
    filter_backends = [OrderingFilter]
    ordering = ["id"]
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "partial_update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateSHGSerializer
        return super().create(request, *args, **kwargs)


class DocumentUploadAPI(ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [OrderingFilter]
    ordering = ["id"]
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "partial_update": [Roles.SUPER_ADMIN, Roles.ADMIN, Roles.CM, Roles.CCM],
        "destroy": [Roles.SUPER_ADMIN],
    }
