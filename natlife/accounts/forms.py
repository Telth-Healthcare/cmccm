from django import forms

from rest_framework.request import Request

from core.constants import Roles

from .models import User, Role


class SignupForm(forms.ModelForm):
    """
    Plugs into allauth via ACCOUNT_SIGNUP_FORM_CLASS.

    Any fields defined here are automatically:
      1. Expected in the POST body of POST /_allauth/app/v1/auth/signup
      2. Validated by Django's form validation before the user is created
      3. Passed to save() after allauth has created and saved the User
    """

    roles = forms.MultipleChoiceField(
        choices=Roles.choices,
        required=True
    )

    class Meta:
        model = User
        fields = "__all__"


    def signup(self, request: Request, user: User):
        """
        Called by allauth AFTER the User object has been created and saved.
        The user instance is passed directly as a parameter.
        """
        user.is_active = True

        roles = Role.objects.filter(name__in=self.cleaned_data.get("roles", []))
        if roles.exists():
            user.roles.set(roles)

        user.save(update_fields=["is_active"])
