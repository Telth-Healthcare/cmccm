from django.urls import path

from .views import ConstantsMetaAPI, SendHtmlMailAPI


urlpatterns = [
    path("app/meta/constants/", ConstantsMetaAPI.as_view()),
    path("app/mail/", SendHtmlMailAPI.as_view()),
]
