from django.conf import settings
from django.utils import timezone
from django.db import transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS
from rest_framework.filters import OrderingFilter

from allauth.account.adapter import get_adapter
from allauth.headless import app_settings as headless_settings
from allauth.headless.tokens.strategies.jwt.strategy import JWTTokenStrategy

from firebase_admin import auth

from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import RoleBasedPermission
from core.constants import Roles

from .models import User, Role, Region, Invitation
from .serializers import (
    RegionSerializer,
    UserSerializer,
    SendInviteSerializer,
    AcceptInviteSerializer,
    FirebaseLoginSerializer
)
from .adapters import CustomAccountAdapter, CustomHeadlessAdapter


ACCEPT_INVITE_URL: str | None = getattr(
    settings,
    "HEADLESS_FRONTEND_URLS",
    {}
).get("accept_invite")


# ─────────────────────────────────────────────
# Region
# ─────────────────────────────────────────────

class RegionViewSet(ModelViewSet):

    queryset = Region.objects.select_related("admin")
    filter_backends = [OrderingFilter]
    ordering = ["-id"]
    serializer_class = RegionSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "create": [Roles.SUPER_ADMIN],
        "update": [Roles.SUPER_ADMIN],
        "partial_update": [Roles.SUPER_ADMIN],
        "destroy": [Roles.SUPER_ADMIN],
    }


# ─────────────────────────────────────────────
# Invitations
# ─────────────────────────────────────────────

class InvitationViewSet(ModelViewSet):

    queryset = Invitation.objects.all()
    serializer_class = SendInviteSerializer
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "create": [],
        "update": [],
        "partial_update": [],
        "destroy": [],
    }


# ─────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
        "roles": ["exact"],
        "roles__name": ["exact", "icontains"],
        "manager": ["exact"],
    }
    ordering = ["-created_at"]
    serializer_class = UserSerializer
    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "list": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "retrieve": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "create": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "update": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "partial_update": [Roles.SUPER_ADMIN, Roles.ADMIN],
        "destroy": [Roles.SUPER_ADMIN],
    }

    def get_queryset(self):

        user: User = self.request.user

        qs = (
            User.objects
            .select_related(
                "region",
                "manager"
            )
            .prefetch_related("roles")
            .exclude(pk=user.pk)
            .exclude(
                roles__in=[
                    Role.objects.get(name=Roles.SUPER_ADMIN).pk
                ]
            )
        )

        if user.has_role(Roles.SUPER_ADMIN):
            return qs

        if user.has_role(Roles.ADMIN):
            return qs.filter(
                region=user.region
            ).exclude(
                roles__in=user.roles.all()
            ).exclude(
                region__isnull=True
            )

        return qs.none()


# ─────────────────────────────────────────────
# Firebase Login
# ─────────────────────────────────────────────

class FirebaseLoginAPIView(APIView):

    permission_classes = []

    def post(self, request: Request):

        serializer = FirebaseLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            decoded_token: dict = auth.verify_id_token(token)
            phone_number = decoded_token.get("phone_number")
        except Exception as e:
            print(e)
            return Response({"detail": "Invalid token."}, status=400)

        if not phone_number:
            return Response({"detail": "No phone number in token."}, status=400)

        adapter: CustomAccountAdapter = get_adapter()
        user = adapter.get_user_by_phone(phone_number)

        if not user:
            return Response({"detail": "User not found."}, status=404)

        adapter.set_phone_verified(user, phone_number)
        adapter.login(request, user)

        strategy: JWTTokenStrategy = headless_settings.TOKEN_STRATEGY
        token_payload = strategy.create_access_token_payload(request)

        return Response({
            "status": 200,
            "data": {
                "user": CustomHeadlessAdapter(request=request).serialize_user(user),
                "methods": [
                    {
                        "method": "firebase",
                        "at": token_payload.get("iat")
                    }
                ],
            },
            "meta": {
                "is_authenticated": True,
                **token_payload
            }
        })


# ─────────────────────────────────────────────
# Send Invite
# ─────────────────────────────────────────────

class SendInviteAPIView(APIView):

    permission_classes = [RoleBasedPermission]

    role_permissions = {
        "post": [Roles.SUPER_ADMIN, Roles.ADMIN]
    }

    @transaction.atomic
    def post(self, request: Request):

        serializer = SendInviteSerializer(
            data=request.data,
            context={"request": request},
            many=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": 201,
            "count": len(serializer.validated_data),
            "data": serializer.data,
        })


# ─────────────────────────────────────────────
# Accept Invite
# ─────────────────────────────────────────────

class AcceptInviteAPIView(APIView):

    permission_classes = []

    @transaction.atomic
    def post(self, request: Request):

        serializer = AcceptInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        invite = Invitation.objects.filter(
            token=token,
            accepted=False
        ).prefetch_related("roles").first()

        if not invite:
            raise ValidationError("Invalid invitation.")

        if invite.expires_at < timezone.now():
            raise ValidationError("Invitation expired.")

        # Prevent duplicate users
        if User.objects.filter(phone=invite.phone).exists():
            raise ValidationError("User already exists.")
        
        user_data = {
            "first_name": invite.first_name,
            "last_name": invite.last_name,
            "email": invite.email,
            "phone": invite.phone,
            "region": invite.region,
            "manager": invite.manager,
            "created_by": invite.invited_by,
            "phone_verified": True,
            "is_active": True,
        }

        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        user.roles.set(invite.roles.all())

        region = Region.objects.filter(pk=invite.region.pk).first()
        if region:
            region.admin = user
            region.save(update_fields=["admin"])

        invite.accepted = True
        invite.save(update_fields=["accepted"])

        redirect_url = getattr(settings, "HEADLESS_FRONTEND_URLS", {}).get("admin_login_url")

        return Response({"detail": "Invitation accepted", "redirect_url": redirect_url})



class JSONRateLimitView(APIView):
    """
    Replaces allauth's HTML rate-limit page with a JSON 429 response.
    Works for both GET (redirect landing) and POST requests.
    """
    authentication_classes = []   # No auth needed — they're already blocked
    permission_classes = []       # Publicly accessible

    def get(self, request, *args, **kwargs):
        return self._rate_limit_response()

    def post(self, request, *args, **kwargs):
        return self._rate_limit_response()

    def _rate_limit_response(self):
        return Response(
            {
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "detail": "You have exceeded the allowed number of attempts. "
                          "Please wait before trying again.",
            },
            status=HTTP_429_TOO_MANY_REQUESTS,
        )
