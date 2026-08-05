from rest_framework.permissions import BasePermission, SAFE_METHODS
from user.models import User


class MenuPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return user.restaurants.exists()

        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return request.method in SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        if user.role == User.RoleChoices.OWNER:
            return obj.restuarant.owner_id == user.id

        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return request.method in SAFE_METHODS and user.restaurant == obj.restuarant

        return False