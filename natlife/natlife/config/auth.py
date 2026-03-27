import os
from datetime import timedelta


AUTH_USER_MODEL = "accounts.User"

SITE_ID = 1
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Telth] "
MFA_TOTP_ISSUER = "Telth"


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# ------------------------------------------------------------------------------
# ADAPTER SETTINGS
# ------------------------------------------------------------------------------
ACCOUNT_ADAPTER = "accounts.adapters.CustomAccountAdapter"
HEADLESS_ADAPTER = "accounts.adapters.CustomHeadlessAdapter"
SOCIALACCOUNT_ADAPTER = "accounts.adapters.SocialAccountAdapter"

# ------------------------------------------------------------------------------
# BASE SETTING
# ------------------------------------------------------------------------------
ACCOUNT_SIGNUP_FORM_CLASS = "accounts.forms.SignupForm"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email", "phone"}
ACCOUNT_SIGNUP_FIELDS = ["phone*","password1",  "email*"]
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False

ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True
ACCOUNT_EMAIL_VERIFICATION_MAX_RESEND_COUNT = 3

ACCOUNT_PHONE_VERIFICATION_ENABLED = True
ACCOUNT_PHONE_VERIFICATION_SUPPORTS_RESEND = True
ACCOUNT_PHONE_VERIFICATION_MAX_RESEND_COUNT = 3
ACCOUNT_PHONE_VERIFICATION_TTL = timedelta(minutes=5).seconds

ACCOUNT_LOGIN_BY_CODE_ENABLED = True


# ------------------------------------------------------------------------------
# HEADLESS
# ------------------------------------------------------------------------------
HEADLESS_ONLY = True
HEADLESS_CLIENTS = ("app",)

HEADLESS_JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
HEADLESS_TOKEN_STRATEGY = "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN = timedelta(hours=4).seconds
HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN = timedelta(days=7).seconds
HEADLESS_JWT_ROTATE_REFRESH_TOKEN = True
HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = True

# ------------------------------------------------------------------------------
# MULTIFACTOR AUTHENTICATION
# ------------------------------------------------------------------------------
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes"]
MFA_RECOVERY_CODE_COUNT = 8
