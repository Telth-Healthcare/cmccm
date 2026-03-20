from ..settings import *
from .auth import *

SECRET_KEY = os.getenv("SECRET_KEY")

APPEND_SLASH = False

DRF_APPS = [
    "rest_framework",
    "rest_framework.authtoken", # MANDATORY FOR INTERNAL COMMUNICATION
    "django_filters",
    "corsheaders",
]

THIRD_PARTY_APPS = [
    "anymail",
    "storages",
]

ALLAUTH_APPS = [
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.mfa",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "shg",
    "applications",
    "admin_panel",
    "website",
    "trainer",
]


INSTALLED_APPS += DRF_APPS + THIRD_PARTY_APPS + ALLAUTH_APPS + LOCAL_APPS

# ------------------------------------------------------------------------------
# TEMPLATE
# ------------------------------------------------------------------------------
TEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "templates"))


# ------------------------------------------------------------------------------
# ALLAUTH MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE.append("allauth.account.middleware.AccountMiddleware")


# ------------------------------------------------------------------------------
# MEDIA SETTING
# ------------------------------------------------------------------------------
MEDIA_URL = "/"
MEDIA_ROOT = "media/"


# ------------------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "allauth.headless.contrib.rest_framework.authentication.JWTTokenAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


# ------------------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------------------
from corsheaders.defaults import default_headers

MIDDLEWARE.insert(2, "corsheaders.middleware.CorsMiddleware")
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "ngrok-skip-browser-warning",
    "x-session-token",
    "x-client-id",
]


# ------------------------------------------------------------------------------
# FIREBASE INITIALIZATION
# ------------------------------------------------------------------------------
import firebase_admin
from firebase_admin import credentials

firebase_config = {
    "type": os.getenv('FIREBASE_TYPE'),
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_config)
default_app = firebase_admin.initialize_app(cred)


# ------------------------------------------------------------------------------
# EMAIL SERVICE SETTINGS
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"


# ------------------------------------------------------------------------------
# HEADLESS FRONTEND URLS
# ------------------------------------------------------------------------------
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": FRONTEND_BASE_URL + "/invite/accept/?key={key}",
    "account_reset_password": FRONTEND_BASE_URL + "/account/password/reset",
    "account_reset_password_from_key": FRONTEND_BASE_URL + "/reset-password/?key={key}",
    "account_signup": FRONTEND_BASE_URL + "/account/signup",
    "socialaccount_login_error": FRONTEND_BASE_URL + "/account/provider/callback",

    "accept_invite": FRONTEND_BASE_URL + "/invite/accept/?key={key}",
    "admin_login_url": "/admin/signin",
    "shg_login_url": FRONTEND_BASE_URL + "/shg-auth/signin",
}


INVITATION_TTL = timedelta(days=7)
CACHE_TTL = timedelta(minutes=30).seconds
