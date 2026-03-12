from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import (
    RegionViewSet,
    InvitationViewSet,
    UserViewSet,
    SendInviteAPIView,
    AcceptInviteAPIView,
    FirebaseLoginAPIView,
    JSONRateLimitView,
)


router = DefaultRouter()
router.register("users", UserViewSet)
router.register("regions", RegionViewSet)
router.register("invitations", InvitationViewSet)


urlpatterns = [
    path("invite/send/", SendInviteAPIView.as_view()),
    path("invite/accept/", AcceptInviteAPIView.as_view()),
    path("firebase/login/", FirebaseLoginAPIView.as_view()),
    path("rate-limit/", JSONRateLimitView.as_view(), name="account_rate_limit"),
] + router.urls
