from rest_framework.routers import DefaultRouter
from django.urls import path, include

from core.views import ConstantsAPIView
from .views import (
    SHGViewSet,
    DocumentUploadAPI,
)


router = DefaultRouter()
router.register("cm-ccm", SHGViewSet)
router.register("documents", DocumentUploadAPI)

urlpatterns = [
    path(
        "constants/",
        ConstantsAPIView.as_view(constants_module="shg.constants"),
        name="shg_constants"
    ),
    path("app/", include(router.urls)),
]
