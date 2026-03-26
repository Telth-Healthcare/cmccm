from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    SHGConstantMetaAPI,
    SHGViewSet,
    DocumentUploadAPI,
)


router = DefaultRouter()
router.register("cm-ccm", SHGViewSet)
router.register("documents", DocumentUploadAPI)

urlpatterns = [
    path("constants/", SHGConstantMetaAPI.as_view()),
    path("app/", include(router.urls)),
]
