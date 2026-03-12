from .base import *


DEBUG = True

ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += [
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
]


# ------------------------------------------------------------------------------
# EMAIL SERVICE SETTINGS
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"
ANYMAIL = {
    "RESEND_API_KEY": os.getenv("RESEND_TEST_API_KEY"),
}

# ------------------------------------------------------------------------------
# CSRF & COOKIE SETTINGS
# ------------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://*.ngrok-free.dev",
    "https://cm-ccm-onboarding.vercel.app",
]
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

CORS_ALLOW_CREDENTIALS = True


# ------------------------------------------------------------------------------
# BACKEND URLS
# ------------------------------------------------------------------------------
if os.getenv("STAGING"):
    CORE_URL = os.getenv("STAGING_CORE_URL")
    ACCOUNTS_URL = os.getenv("STAGING_ACCOUNTS_URL")
    SHG_URL = os.getenv("STAGING_SHG_URL")
    APPLICATIONS_URL = os.getenv("STAGING_APPLICATIONS_URL")
    ADMIN_PANEL_URL = os.getenv("STAGING_ADMIN_PANEL_URL")
else:
    CORE_URL = "http://127.0.0.1:8000"
    ACCOUNTS_URL = "http://127.0.0.1:8000"
    SHG_URL = "http://127.0.0.1:8000"
    APPLICATIONS_URL = "http://127.0.0.1:8000"
    ADMIN_PANEL_URL = "http://127.0.0.1:8000"
