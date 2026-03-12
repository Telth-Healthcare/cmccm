import requests

from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache

from rest_framework.authtoken.models import Token

from allauth.account.adapter import DefaultAccountAdapter
from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress

from .models import User
from .serializers import UserSerializer


APPLICATIONS_BACKEND_URL = getattr(settings, "APPLICATIONS_URL")
SHG_BACKEND_URL = getattr(settings, "SHG_URL")
OTP_TTL = getattr(settings, "ACCOUNT_PHONE_VERIFICATION_TTL")


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Hooks into allauth's account layer.

    get_email_confirmation_url: overrides where the "Confirm Email" link
    in verification emails points. By default allauth points to its own
    server-rendered view — we redirect to the SPA instead.
    """

    def confirm_email(self, request, email_address: EmailAddress):
        super().confirm_email(request, email_address)
        return email_address

    def get_phone(self, user: User):
        return user.phone, user.phone_verified

    def set_phone(self, user: User, phone: str, verified: bool):
        user.phone = phone
        user.phone_verified = verified
        user.save(update_fields=["phone", "phone_verified"])

    def set_phone_verified(self, user: User, phone):
        updating_fields = ["phone_verified"]
        if not user.is_active:
            user.is_active = True
            updating_fields.append("is_active")
        user.phone_verified = True
        user.save(update_fields=updating_fields)

    def get_user_by_phone(self, phone):
        return User.objects.filter(phone=phone).first()

    def generate_phone_verification_code(self, *, user, phone):
        return get_random_string(length=6, allowed_chars='0123456789')

    def phone_otp_key(self, phone):
        return f"phone-otp:{phone}"

    def otp_attempt_key(self, phone):
        return f"phone-otp-attempts:{phone}"

    def send_verification_code_sms(self, user: User, phone: str, code: str, **kwargs):
        key = self.phone_otp_key(phone)
        cache.set(key, code, timeout=OTP_TTL)
        print(f"[SMS] {phone} → OTP: {code}")

    def verify_phone(self, user, phone, code):
        otp_key = self.phone_otp_key(phone)
        attempts_key = self.otp_attempt_key(phone)

        cached_code = cache.get(otp_key)
        if not cached_code:
            return False

        attempts = cache.get(attempts_key, 0)
        if attempts >= 5:
            return False

        if cached_code != code:
            cache.set(attempts_key, attempts + 1, timeout=300)
            return False

        cache.delete(otp_key)
        cache.delete(attempts_key)
        self.set_phone_verified(user, phone)
        return True


class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    """
    Controls the shape of the `user` payload in every headless API response.

    Whenever allauth returns user data (after login, signup, session check, etc.)
    it calls serialize_user(). This is the single place to control what your
    frontend receives — no separate UserSerializer needed.
    """

    def get_user_token(self, user: User):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def get_application_status(self, user: User):
        token = self.get_user_token(user)
        application_status = None
        try:
            user_applications = user.applications
        except Exception:
            user_applications = None

        if user_applications:
            url = f"{APPLICATIONS_BACKEND_URL}/applications/app/{user.applications.pk}/"
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Token {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            if response.status_code == 200:
                response_data = response.json()
                application_status = {
                    "id": user.applications.pk,
                    "reference_number": response_data["reference_number"],
                    "status": response_data["status"],
                }
        
        return application_status


    def serialize_user(self, user: User):

        try:
            shg_id = user.shg.id
        except Exception:
            shg_id = None

        return {
            **UserSerializer(user).data,
            "application_status": self.get_application_status(user),
            "profile_id": shg_id,
        }


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    pass
