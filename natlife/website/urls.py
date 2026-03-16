from rest_framework.routers import DefaultRouter

from .views import ContactViewSet, WebinarViewSet

router = DefaultRouter()
router.register("contacts", ContactViewSet, basename="contacts")
router.register("webinars", WebinarViewSet, basename="webinars")

urlpatterns = router.urls
