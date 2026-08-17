from rest_framework.permissions import BasePermission

from user.models import User

class RolePermission(BasePermission):
    message = "Only platform admins and restaurant owners can manage users."

    def has_permission(self, request, view):
        return request.user.role in [
            User.RoleChoices.PLATFORM_ADMIN,
            User.RoleChoices.OWNER,
        ]

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return (
                obj.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]
                and obj.restaurant is not None
                and obj.restaurant.owner_id == user.id
            )

        return False

class ChangePasswordPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.RoleChoices.PLATFORM_ADMIN, User.RoleChoices.OWNER, User.RoleChoices.WAITER, User.RoleChoices.CHEF]
