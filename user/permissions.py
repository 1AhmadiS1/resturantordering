from rest_framework.permissions import BasePermission

from user.models import User

class RolePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role=='platform_admin':
            return True
        elif request.user.role=='owner':
            return True
        elif request.user.role=='waiter' or request.user.role=='chef':
            return False
        else:
            return False

class ChangePasswordPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.RoleChoices.PLATFORM_ADMIN, User.RoleChoices.OWNER, User.RoleChoices.WAITER, User.RoleChoices.CHEF]
