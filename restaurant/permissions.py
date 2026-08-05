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

        elif user.role in[User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return request.method in SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return True

        elif user.role == User.RoleChoices.OWNER:
            return obj.owner_id == user.id
        
        elif user.role in [User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return user.restaurant_id == obj.id
            
        return False
