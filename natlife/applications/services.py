from core.services import ActivityService, CoreService

from .constants import ApplicationStatus

from .models import Application


ALLOWED_TRANSITIONS = {
    ApplicationStatus.SUBMITTED: [
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.REJECTED,
    ],
    ApplicationStatus.UNDER_REVIEW: [
        ApplicationStatus.ASSIGNED,
        ApplicationStatus.REJECTED,
    ],
    ApplicationStatus.ASSIGNED: [
        ApplicationStatus.TRAINING,
    ],
    ApplicationStatus.TRAINING: [
        ApplicationStatus.PRODUCTION,
    ],
    ApplicationStatus.PRODUCTION: [],
    ApplicationStatus.REJECTED: [],
}


class ApplicationService:

    @staticmethod
    def generate_reference_number():
        year = CoreService.current_year()

        last_application = Application.objects.filter(
            created_at__year=year
        ).order_by(
            "-reference_number"
        ).first()
        last_ref_no = last_application.reference_number.split(
            "-"
        )[-1] if last_application else "0000"
        count = int(last_ref_no) + 1

        return f"CM-{year}-{str(count).zfill(4)}"

    @staticmethod
    def create_application(actor, application: Application):

        ActivityService.log(
            actor=actor,
            action="application_created",
            object_type="Application",
            object_id=application.pk,
        )

        return application

    @staticmethod
    def update_application(actor, application: Application):

        ActivityService.log(
            actor=actor,
            action="application_updated",
            object_type="Application",
            object_id=application.pk
        )

        return application

    @staticmethod
    def update_status(actor, application: Application, new_status):

        ActivityService.log(
            actor=actor,
            action="status_changed",
            object_type="Application",
            object_id=application.pk,
            metadata={
                "old_status": application.status,
                "new_status": new_status,
            },
        )
