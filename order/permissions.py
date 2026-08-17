from rest_framework.permissions import BasePermission, SAFE_METHODS

from user.models import User


class OrderPermission(BasePermission):
    message = "Your role is not allowed to perform this action on orders."

    def has_permission(self, request, view):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return True

        if user.role == User.RoleChoices.WAITER:
            return request.method in [*SAFE_METHODS, "POST", "PUT", "PATCH"]

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
            return (
                request.method in [*SAFE_METHODS, "PUT", "PATCH"]
                and obj.restuarant_id == user.restaurant_id
            )

        if user.role == User.RoleChoices.CHEF:
            return (
                request.method in [*SAFE_METHODS, "PATCH"]
                and obj.restuarant_id == user.restaurant_id
            )

        return False
