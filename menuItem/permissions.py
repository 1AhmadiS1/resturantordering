from rest_framework.permissions import BasePermission,SAFE_METHODS
from user.models import User


class MenuItemPermission(BasePermission):
    message = "Your role is not allowed to perform this action on menu items."

    def has_permission(self, request, view):
        user= request.user
        if user.role== User.RoleChoices.PLATFORM_ADMIN:
            return True
        elif user.role== User.RoleChoices.OWNER:
            return True
        elif user.role in [User.RoleChoices.WAITER,User.RoleChoices.CHEF]:
            return request.method in SAFE_METHODS
        return False
    def has_object_permission(self, request, view, obj):
        user= request.user
        if user.role== User.RoleChoices.PLATFORM_ADMIN:
            return True
        elif user.role== User.RoleChoices.OWNER and obj.menu.restuarant.owner==user:
            return True
        elif user.role in [User.RoleChoices.WAITER,User.RoleChoices.CHEF] and user.restaurant==obj.menu.restuarant:
            return request.method in SAFE_METHODS
        return False
