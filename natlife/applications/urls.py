from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import ConstantsAPIView

from applications.views import (
    ApplicationViewSet,
    ApplicationActivityLogAPIView,
)

router = DefaultRouter()
router.register("app", ApplicationViewSet)


urlpatterns = [
    path(
        "constants/", 
        ConstantsAPIView.as_view(constants_module="applications.constants"), 
        name="application-constants"
    ),
    path(
        "app/logs/",
        ApplicationActivityLogAPIView.as_view({"get": "list"}),
        name="application-logs",
    ),
    path("", include(router.urls)),
]
