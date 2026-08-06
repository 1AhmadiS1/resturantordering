from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
# pyrefly: ignore [missing-import]
from menuItem.permissions import MenuItemPermission
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
# pyrefly: ignore [missing-import]
from .models import MenuItem
# pyrefly: ignore [missing-import]
from .serializer import MenuItemSerializer
from user.models import User
from menu.models import Menu
# Create your views here.
@extend_schema_view(
    list=extend_schema(tags=["MenuItems"]),
    retrieve=extend_schema(tags=["MenuItems"]),
    create=extend_schema(tags=["MenuItems"]),
    update=extend_schema(tags=["MenuItems"]),
    partial_update=extend_schema(tags=["MenuItems"]),
    destroy=extend_schema(tags=["MenuItems"]),
)
class MenuItemViewSet(ModelViewSet):
    serializer_class=MenuItemSerializer
    permission_classes=[IsAuthenticated,MenuItemPermission]
    def get_queryset(self):
        user=self.request.user
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return MenuItem.objects.all()
        elif user.role== User.RoleChoices.OWNER:
            return MenuItem.objects.filter(menu__restuarant__owner=user)
        elif user.role in [User.RoleChoices.WAITER,User.RoleChoices.CHEF]:
            return MenuItem.objects.filter(menu__restuarant=user.restaurant)
        return MenuItem.objects.none()
