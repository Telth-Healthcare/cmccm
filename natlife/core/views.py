import importlib
import inspect

from django.db import models

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.authentication import TokenAuthentication

from .constants import Roles
from .services import CoreService
from .permissions import RoleBasedPermission
from .serializers import EmailSerializer


class ConstantsAPIView(APIView):
    """
    Base view for exposing TextChoices constants from a module.

    Usage:
        class TrainerConstantsAPI(ConstantsAPIView):
            constants_module = "trainer.constants"
    """
    permission_classes = []
    constants_module: str = None

    def get(self, request):
        if not self.constants_module:
            raise NotImplementedError("Subclasses must define `constants_module`.")

        data = CoreService.get_constants(self.constants_module)
        return Response(data)


class ConstantsMetaAPI(APIView):
    permission_classes = []

    def get(self, request: Request, *args, **kwargs):
        return Response({
            **CoreService.get_constants("core.constants"),
            **CoreService.get_constants("shg.constants"),
            **CoreService.get_constants("applications.constants"),
            **CoreService.get_constants("trainer.constants"),
        })


class SendHtmlMailAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "post": [Roles.SUPER_ADMIN, Roles.ADMIN],
    }

    def post(self, request: Request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            CoreService.send_mail(
                subject=serializer.validated_data["subject"],
                html_content=serializer.validated_data["html_content"],
                text_content=serializer.validated_data["text_content"],
                to=serializer.validated_data["to"],
            )
            return Response({"message": "Email sent successfully"}, status=HTTP_200_OK)

        return Response({
            "message": "Error sending email",
            "errors": serializer.errors,
        }, status=HTTP_400_BAD_REQUEST)
