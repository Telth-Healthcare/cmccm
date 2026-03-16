from .base import *


DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

# ------------------------------------------------------------------------------
# RESTFRAMEWORK SETTINGS
# ------------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]

# ------------------------------------------------------------------------------
# EMAIL SERVICE SETTINGS
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = "no-reply@mytelth.com"
ANYMAIL = {
    "RESEND_API_KEY": os.getenv("RESEND_API_KEY"),
}

# ------------------------------------------------------------------------------
# CSRF & COOKIE SETTINGS
# ------------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://api.telth.care",
    "https://partner.telth.care",
    "https://admin.telth.care",
]
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
CORS_ALLOW_CREDENTIALS = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ------------------------------------------------------------------------------
# BACKEND URLS
# ------------------------------------------------------------------------------
CORE_URL = os.getenv("CORE_URL", "http://127.0.0.1:8000")
ACCOUNTS_URL = os.getenv("ACCOUNTS_URL", "http://127.0.0.1:8000")
SHG_URL = os.getenv("SHG_URL", "http://127.0.0.1:8000")
APPLICATIONS_URL = os.getenv("APPLICATIONS_URL", "http://127.0.0.1:8000")
ADMIN_PANEL_URL = os.getenv("ADMIN_PANEL_URL", "http://127.0.0.1:8000")

# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(os.getenv('SUPABASE_DB'))
}

# ------------------------------------------------------------------------------
# STORAGE SERVICE SETTINGS
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "static",
        },
    },
}
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
MEDIA_URL  = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
