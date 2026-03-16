from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from core.permissions import RoleBasedPermission
from core.constants import Roles

from .models import Contact
from .serializers import ContactSerializer, WebinarSerializer


class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all().order_by("-id")
    serializer_class = ContactSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN],
        "retrieve": [Roles.SUPER_ADMIN],
        "create": [Roles.SUPER_ADMIN],
        "update": [Roles.SUPER_ADMIN],
        "partial_update": [Roles.SUPER_ADMIN],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        return super().get_queryset().exclude(name__isnull=True)


class WebinarViewSet(ModelViewSet):
    queryset = Contact.objects.all().order_by("-id")
    serializer_class = WebinarSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN],
        "retrieve": [Roles.SUPER_ADMIN],
        "create": [Roles.SUPER_ADMIN],
        "update": [Roles.SUPER_ADMIN],
        "partial_update": [Roles.SUPER_ADMIN],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        return super().get_queryset().exclude(name__isnull=False)
