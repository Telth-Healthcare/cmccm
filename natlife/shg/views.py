from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter

from core.permissions import RoleBasedPermission
from core.constants import Roles

from .models import SHG, Document
from .serializers import (
    CreateSHGSerializer,
    SHGSerializer,
    DocumentSerializer,
)


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
