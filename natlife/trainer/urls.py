from rest_framework.routers import DefaultRouter

from .views import (
    ProfileViewSet,
    CourseViewSet,
    CourseEnrollmentViewSet,
    CourseMaterialViewSet,
)


router = DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("courses", CourseViewSet)
# router.register("course-enrollments", CourseEnrollmentViewSet)
# router.register("course-materials", CourseMaterialViewSet)

urlpatterns = router.urls
app_name = "trainer"
app_label = "trainer"
namespace = "trainer"
