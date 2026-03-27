class TrainerService:
    """
    Service class to handle business logic for Trainer related operations.
    """

    @staticmethod
    def get_trainer_dashboard_stats(trainer_user):
        """
        Returns statistics for a specific trainer.
        """
        from .models import Course, CourseEnrollment
        
        courses = Course.objects.filter(created_by=trainer_user)
        course_ids = courses.values_list('id', flat=True)
        
        return {
            "total_courses": courses.count(),
            "total_enrollments": CourseEnrollment.objects.filter(course_id__in=course_ids).count(),
            "active_students": CourseEnrollment.objects.filter(course_id__in=course_ids).values('user').distinct().count()
        }
