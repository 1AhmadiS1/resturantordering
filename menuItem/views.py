from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
# pyrefly: ignore [missing-import]
from menuItem.permissions import MenuItemPermission
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["menu", "category"]
    search_fields = ["name", "description", "category", "menu__name"]
    ordering_fields = ["id", "name", "category", "price", "created_at", "updated_at"]
    ordering = ["id"]

    def get_queryset(self):
        user=self.request.user
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return MenuItem.objects.all().order_by("name")
        elif user.role== User.RoleChoices.OWNER:
            return MenuItem.objects.filter(menu__restuarant__owner=user).order_by("name")
        elif user.role in [User.RoleChoices.WAITER,User.RoleChoices.CHEF]:
            return MenuItem.objects.filter(menu__restuarant=user.restaurant).order_by("name")
        return MenuItem.objects.none()
