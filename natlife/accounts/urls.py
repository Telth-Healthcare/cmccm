from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import (
    RegionViewSet,
    UserViewSet,
    SendInviteAPIView,
    ResendInviteAPIView,
    AcceptInviteAPIView,
    FirebaseLoginAPIView,
    JSONRateLimitView,
)


router = DefaultRouter()
router.register("users", UserViewSet)
router.register("regions", RegionViewSet)


urlpatterns = [
    path("invite/send/", SendInviteAPIView.as_view()),
    path("invite/resend/", ResendInviteAPIView.as_view(), name="invite_resend"),
    path("invite/accept/", AcceptInviteAPIView.as_view()),
    path("firebase/login/", FirebaseLoginAPIView.as_view()),
    path("rate-limit/", JSONRateLimitView.as_view(), name="account_rate_limit"),
] + router.urls
