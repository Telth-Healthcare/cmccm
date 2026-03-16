"""
URL configuration for natlife project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("_accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("shg/", include("shg.urls")),
    path("applications/", include("applications.urls")),
    path("admin/", include("admin_panel.urls")),
    path("web/", include("website.urls")),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
