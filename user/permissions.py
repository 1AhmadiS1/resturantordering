from rest_framework.permissions import BasePermission

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