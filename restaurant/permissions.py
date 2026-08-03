from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from user.models import User


class RestaurantPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return request.method in [*SAFE_METHODS, "PUT", "PATCH", "DELETE"]

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return obj.owner_id == user.id

        return False