from .constants import Roles
from .serializers import ActivityLogSerializer


class RoleBasedFilterBase:

    def admin_filter(self, user) -> dict | None:
        return {"user__manager": user}

    def financier_filter(self, user) -> dict | None:
        return {"assigned_financier": user}

    def trainer_filter(self, user) -> dict | None:
        return {"assigned_trainer": user}

    def partner_filter(self, user) -> dict | None:
        return {"user": user}

    def get_filter_map(self):
        return [
            (Roles.SUPER_ADMIN, None),
            (Roles.ADMIN, self.admin_filter),
            (Roles.FINANCIER, self.financier_filter),
            (Roles.TRAINER, self.trainer_filter),
            (Roles.CM, self.partner_filter),
            (Roles.CCM, self.partner_filter),
        ]



class RoleFilteredQuerysetMixin(RoleBasedFilterBase):
    """
    Filters querysets based on the requesting user's role.

    Usage: define any of the filter methods below in your ViewSet.
    Each method receives the requesting user and must return a dict
    of filter kwargs to apply to the queryset.

    Example:
        def admin_filter(self, user):
            return {"created_by__region": user.region}

        def trainer_filter(self, user):
            return {"created_by": user}
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        for role, filter_fn in self.get_filter_map():
            if user.has_role(role):
                if filter_fn is None:
                    return qs  # SUPER_ADMIN: unfiltered
                filters = filter_fn(user)
                return qs.filter(**filters).distinct() if filters else qs.none()

        return qs.none()


class RoleBasedLogFilterMixin(RoleBasedFilterBase):
    """
    Filters activity logs based on the requesting user's role and 
    the object type they are allowed to see.
    """
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        for role, filter_fn in self.get_filter_map():
            if user.has_role(role):
                if filter_fn is None:
                    return qs  # SUPER_ADMIN: unfiltered
                filters = filter_fn(user)
                app_ids = self.model.objects.filter(
                    **filters
                ).values_list("pk", flat=True)

                return qs.filter(object_id__in=app_ids)

        return qs.none()
