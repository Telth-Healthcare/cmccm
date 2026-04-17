import uuid
import importlib
import inspect
import requests
from pathlib import Path

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from anymail.exceptions import AnymailRequestsAPIError


from .models import ActivityLog
from .serializers import EmailSerializer

EMAIL_HOST_USER = getattr(settings, "EMAIL_HOST_USER")
ACCOUNTS_URL = getattr(settings, "ACCOUNTS_URL")
SHG_URL =  getattr(settings, "SHG_URL")
APPLICATIONS_URL = getattr(settings, "APPLICATIONS_URL")
TRAINER_URL = getattr(settings, "TRAINER_URL")
ADMIN_PANEL_URL = getattr(settings, "ADMIN_PANEL_URL")


class ActivityService:
    @staticmethod
    def log(actor, action, object_type, object_id, metadata=None):
        ActivityLog.objects.create(
            actor=actor,
            action=action,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata or {},
        )

    @staticmethod
    def get_logs():
        return ActivityLog.objects.all()


class CoreService:

    @staticmethod
    def send_mail(
        subject: str,
        html_content: str,
        text_content: str,
        to: str,
        *args,
        **kwargs
    ):
        serializer = EmailSerializer(
            data={
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content,
                "to": to,
            }
        )
        serializer.is_valid(raise_exception=True)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_HOST_USER,
            to=[to]
        )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send(fail_silently=False)
            return True
        except AnymailRequestsAPIError:
            return False

    @staticmethod
    def get_constants(module_path: str) -> dict:
        module = importlib.import_module(module_path)

        text_choices_classes = {
            name: cls
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, models.TextChoices)
            and cls.__module__ == module_path
        }

        response_data = {}

        for name, cls in text_choices_classes.items():
            key = ''.join(
                ['_' + c.lower() if c.isupper() else c for c in name]
            ).lstrip('_')

            response_data[key] = [
                {"value": c.value, "label": c.label} for c in cls
            ]

        return response_data

    @staticmethod
    def get_role_constants():
        CONSTANTS_MODULE = "core.constants"
        module = importlib.import_module(CONSTANTS_MODULE)
        text_choices_classes = {
            name: cls
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, models.TextChoices) and cls.__module__ == CONSTANTS_MODULE
        }
        response_data = {}
        for name, cls in text_choices_classes.items():
            key = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
            response_data[key] = [{"value": c.value, "label": c.label} for c in cls]
        return response_data

    @staticmethod
    def get_accounts_constants():
        url = f"{ACCOUNTS_URL}/accounts/constants/"
        response = requests.get(url)
        return response.json()

    @staticmethod
    def get_shg_constants():
        url = f"{SHG_URL}/partners/constants/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    @staticmethod
    def get_applications_constants():
        url = f"{APPLICATIONS_URL}/applications/constants/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    @staticmethod
    def get_trainer_constants():
        url = f"{APPLICATIONS_URL}/trainer/constants/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    @staticmethod
    def current_year():
        return timezone.now().year

    @staticmethod
    def create_uuid_filename(original_path_str: str) -> str:
        """
        Takes an original file path string, inserts a UUID before the filename,
        and returns the new, dynamic file path string.

        Args:
            original_path_str: The full path to the file (e.g., "banners/image.jpg").

        Returns:
            The new file path with a UUID prepended to the filename 
            (e.g., "banners/a1b2c3d4-xxxx-yyyy-zzzz-1234567890ab-image.jpg").
        """
        # Use pathlib for clean, OS-agnostic path handling
        original_path = Path(original_path_str)

        # 1. Get the path to the parent directory (e.g., 'banners')
        parent_dir = original_path.parent

        # 2. Get the file's original name including the extension (e.g., 'image.jpg')
        original_filename = original_path.name

        # 3. Generate a UUID
        uid = uuid.uuid4()

        # 4. Construct the new filename with the UUID prepended
        new_filename = f"{uid}_{original_filename}"

        # 5. Join the parent directory and the new filename to form the new path
        new_path = parent_dir / new_filename

        # Return the new path as a string
        return str(new_path).replace("\\", "/")
