from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    TrainerConstantsAPI,
    ProfileViewSet,
    CourseViewSet,
    SubjectViewSet,
    SubjectMaterialViewSet,
    CourseEnrollmentViewSet,
    GroupEnrollmentView,
    GroupViewSet,
)


router = DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("courses", CourseViewSet)
router.register("subjects", SubjectViewSet)
router.register("subject-materials", SubjectMaterialViewSet)
router.register("course-enrollments", CourseEnrollmentViewSet)
router.register("groups", GroupViewSet)

urlpatterns = [
    path("app/", include(router.urls)),
    path("constants/", TrainerConstantsAPI.as_view(), name="constants"),

    path("app/group-enrollments/", GroupEnrollmentView.as_view(), name="group-enrollments")
]
