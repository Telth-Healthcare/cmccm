import dj_database_url
from .local import *


DATABASES = {
    "default": dj_database_url.parse(os.getenv("STAGING_SUPABASE_DB"))
}


SUPABASE_CONFIG = {
    "SUPABASE_URL": os.getenv("STAGING_SUPABASE_URL"),
    "SUPABASE_KEY": os.getenv("STAGING_SUPABASE_KEY"),
    "SUPABASE_BUCKET": os.getenv("STAGING_SUPABASE_BUCKET"),
}


STORAGES = {
    "default": {
        "BACKEND": "core.storage.SupabaseMediaStorage",
    },

    "staticfiles": {}
}


REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]


CSRF_TRUSTED_ORIGINS += [
    "https://cm-ccm-onboarding.vercel.app",
    "https://cmccm.vercel.app",
]
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS


CORE_URL = os.getenv("STAGING_CORE_URL")
ACCOUNTS_URL = os.getenv("STAGING_ACCOUNTS_URL")
SHG_URL = os.getenv("STAGING_SHG_URL")
APPLICATIONS_URL = os.getenv("STAGING_APPLICATIONS_URL")
TRAINER_URL = os.getenv("STAGING_TRAINER_URL")
ADMIN_PANEL_URL = os.getenv("STAGING_ADMIN_PANEL_URL")
