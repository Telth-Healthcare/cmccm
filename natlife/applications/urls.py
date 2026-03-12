from django.urls import path, include

from rest_framework.routers import DefaultRouter

from applications.views import (
    ApplicationConstantsAPI,
    ApplicationViewSet,
)

router = DefaultRouter()
router.register("app", ApplicationViewSet)


urlpatterns = [
    path("constants/", ApplicationConstantsAPI.as_view(), name="application-constants"),
    path("", include(router.urls)),
]
