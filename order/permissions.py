from rest_framework.permissions import BasePermission, SAFE_METHODS

from user.models import User


class OrderPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.role in [User.RoleChoices.PLATFORM_ADMIN, User.RoleChoices.OWNER]:
            return True

        if user.role == User.RoleChoices.WAITER:
            return True

        if user.role == User.RoleChoices.CHEF:
            return request.method in [*SAFE_METHODS, "PATCH"]

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return obj.restuarant.owner == user

        if user.role == User.RoleChoices.WAITER:
            return obj.restuarant == user.restaurant

        if user.role == User.RoleChoices.CHEF:
            return request.method in [*SAFE_METHODS, "PATCH"] and obj.restuarant == user.restaurant

        return False
