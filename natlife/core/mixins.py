from .constants import Roles


class RoleFilteredQuerysetMixin:
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

    def admin_filter(self, user) -> dict | None:
        return None

    def trainer_filter(self, user) -> dict | None:
        return None

    def partner_filter(self, user) -> dict | None:
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        role_filter_map = [
            (Roles.SUPER_ADMIN, None),
            (Roles.ADMIN, self.admin_filter),
            (Roles.TRAINER, self.trainer_filter),
            (Roles.CM, self.partner_filter),
            (Roles.CCM, self.partner_filter),
        ]

        for role, filter_fn in role_filter_map:
            if user.has_role(role):
                if filter_fn is None:
                    return qs  # SUPER_ADMIN: unfiltered
                filters = filter_fn(user)
                return qs.filter(**filters).distinct() if filters else qs.none()

        return qs.none()
