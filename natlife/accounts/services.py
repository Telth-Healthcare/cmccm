from django.template.loader import render_to_string
from django.conf import settings


from core.services import ActivityService, CoreService

from .models import User, Invitation


ACCEPT_INVITE_URL: str | None = getattr(
    settings,
    "HEADLESS_FRONTEND_URLS",
    {}
).get("accept_invite")
INVITE_TTL = getattr(settings, "INVITATION_TTL")


class RoleService:

    @staticmethod
    def get_user_roles(user: User):
        return user.roles.all()

    @staticmethod
    def assign_role(actor: User, target_user: User, role_name):

        ActivityService.log(
            actor=actor,
            action="role_assigned",
            object_type="User",
            object_id=target_user.pk,
            metadata={"role": role_name},
        )

    @staticmethod
    def remove_role(actor: User, target_user: User, role_name):

        ActivityService.log(
            actor=actor,
            action="role_removed",
            object_type="User",
            object_id=target_user.pk,
            metadata={"role": role_name},
        )


class AccountServices:

    @staticmethod
    def send_invitation(request, invite: Invitation) -> dict:

        if ACCEPT_INVITE_URL is None:
            raise Exception("ACCEPT_INVITE_URL is not set")

        invite_url = ACCEPT_INVITE_URL.format(key=invite.token)

        return CoreService.send_mail(
            request=request,
            subject="Invitation to join Telth",
            to=invite.email,
            html_content=render_to_string(
                "core/invite.html",
                {
                    "role": invite.roles.first(),
                    "invite_link": invite_url,
                    "expires_in": INVITE_TTL.__str__().split(", ")[0],
                    "expires_on": invite.expires_at.strftime("%B %d, %Y"),
                    "expires_time": invite.expires_at.strftime("%I:%M %p"),
                },
            ),
            text_content=(
                f"Hi {invite.first_name},\n\n"
                f"You have been invited to join Telth.\n\n"
                f"{invite_url}\n\n"
            )
        )
