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
        obj_is_document = getattr(obj, "shg", None)

        if user.is_superuser or user.has_role(Roles.SUPER_ADMIN):
            return True

        if user.role_names.intersection({Roles.ADMIN}):
            if obj_user:
                print("Object user:", obj_user)
                print("Manager:", obj_user.manager)
                return obj_user.manager == user
            elif obj_is_document:
                return obj_is_document.user.manager == user
            return True

        elif user.has_role(Roles.FINANCIER) or user.has_role(Roles.TRAINER):
            application = getattr(obj_user, "applications", None)
            course_user = getattr(obj, "created_by", None)
            subject_user = getattr(obj, "course", None)
            subject_material = getattr(obj, "subject", None)

            if application:
                return self._check_object_permission(
                    application.assigned_financier, user
                ) or self._check_object_permission(
                    application.assigned_trainer, user
                )
            elif course_user:
                return self._check_object_permission(course_user, user)
            elif subject_user:
                return self._check_object_permission(subject_user.created_by, user)
            elif subject_material:
                return self._check_object_permission(subject_material.subject.course.created_by, user)

        elif user.has_role(Roles.CM) or user.has_role(Roles.CCM):
            if obj_user:
                return self._check_object_permission(obj_user, user)
            elif obj_is_document:
                return self._check_object_permission(obj_is_document.user, user)

        if obj_user and self._check_object_permission(obj_user, user):
            return False

        return False


    @staticmethod
    def _check_object_permission(object_user, accessing_user):
        if object_user == accessing_user:
            return True
        return False
