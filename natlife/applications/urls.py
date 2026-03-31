from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import ConstantsAPIView

from applications.views import (
    ApplicationViewSet,
)

router = DefaultRouter()
router.register("app", ApplicationViewSet)


urlpatterns = [
    path(
        "constants/", 
        ConstantsAPIView.as_view(constants_module="applications.constants"), 
        name="application-constants"
    ),
    path("", include(router.urls)),
]
