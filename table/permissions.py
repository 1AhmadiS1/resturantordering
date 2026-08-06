from rest_framework.permissions import SAFE_METHODS
from user.models import User
from rest_framework.permissions import BasePermission

class TablePermission(BasePermission):
    def has_permission(self, request, view):
        user =request.user
        if user.role in [User.RoleChoices.PLATFORM_ADMIN, User.RoleChoices.OWNER]:
            return True

        if user.role == User.RoleChoices.WAITER:
            return request.method in SAFE_METHODS
        return False
    def has_object_permission(self, request, view, obj):
        user =request.user
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True
        if user.role == User.RoleChoices.OWNER:
            return obj.restaurant.owner == user
        if user.role == User.RoleChoices.WAITER:
            return obj.restaurant == user.restaurant
        return False
        