from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import ConstantsAPIView

from .views import (
    ProfileViewSet,
    CourseViewSet,
    CourseCompletionViewSet,
    SubjectViewSet,
    SubjectMaterialViewSet,
    MaterialCompletionViewSet,
    CourseEnrollmentViewSet,
    GroupEnrollmentView,
    GroupViewSet,
)


router = DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("courses", CourseViewSet)
router.register("course-completions", CourseCompletionViewSet)
router.register("subjects", SubjectViewSet)
router.register("subject-materials", SubjectMaterialViewSet)
router.register("material-completions", MaterialCompletionViewSet, basename="material-completion")
router.register("course-enrollments", CourseEnrollmentViewSet)
router.register("groups", GroupViewSet)

urlpatterns = [
    path("app/", include(router.urls)),
    path(
        "constants/",
        ConstantsAPIView.as_view(constants_module="trainer.constants"),
        name="trainer_constants"
    ),

    path("app/group-enrollments/", GroupEnrollmentView.as_view(), name="group-enrollments")
]
