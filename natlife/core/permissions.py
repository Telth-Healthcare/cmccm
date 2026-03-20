import json
from django.http import HttpRequest

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.exceptions import NotAuthenticated

from .constants import Roles


class RoleBasedPermission(BasePermission):
    """
    Universal permission class.

    Reads role permissions from the view:

    role_permissions = {
        "create": ["admin"],
        "list": ["admin", "trainer"],
    }
    """

    def has_permission(self, request: HttpRequest | Request, view):

        user = request.user

        if not user.is_authenticated or not user:
            raise NotAuthenticated("Authentication credentials were not provided.")

        if user.has_role(Roles.SUPER_ADMIN):
            return True

        # Determine action
        action = getattr(view, "action", None)

        # debug_dataset = {
        #     "action": str(action),
        #     "action_map": str(hasattr(view, "action_map")),
        #     "action is None | has action_map": str(action is None and hasattr(view, "action_map")),
        #     "action is None | has action_map | has request method": str(action is None and hasattr(view, "action_map") and getattr(request, "method", None)),
        #     "request.method": str(getattr(request, "method", None)),
        #     "user": str(user),
        #     "user.role_names": str(user.role_names),
        #     "allowed_roles": str(getattr(view, "role_permissions", {}).get(action)),
        # }
        # print(json.dumps(debug_dataset, indent=4))

        if action is None and not hasattr(view, "action_map"):
            action = request.method.lower()
        allowed_roles = getattr(view, "role_permissions", {}).get(action)

        if not allowed_roles:
            return False

        return bool(user.role_names.intersection(allowed_roles))


    def has_object_permission(self, request, view, obj):

        user = request.user
        obj_user = getattr(obj, "user", None)

        if user.is_superuser or user.has_role(Roles.SUPER_ADMIN):
            return True

        if obj_user and obj_user != user:
            return False

        if user.role_names.intersection({Roles.ADMIN, Roles.TRAINER, Roles.CM, Roles.CCM}):
            obj_region = getattr(obj, "region", None)
            if obj_region:
                return obj_region == user.region
            return True

        return False
