from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
# pyrefly: ignore [missing-import]
from menuItem.permissions import MenuItemPermission
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
# pyrefly: ignore [missing-import]
from .models import MenuItem
# pyrefly: ignore [missing-import]
from .serializer import MenuItemSerializer
from user.models import User
# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=["Menu Items"],
        summary="List visible menu items",
        description="Return menu items from restaurants visible to the authenticated user.",
    ),
    retrieve=extend_schema(
        tags=["Menu Items"],
        summary="Get a menu item",
        description="Return one visible menu item with readable menu and restaurant names.",
    ),
    create=extend_schema(
        tags=["Menu Items"],
        summary="Create a menu item",
        description=(
            "Platform admins may add an item to any menu. Owners may add an item only "
            "to a menu belonging to their restaurant. Price must be greater than zero."
        ),
    ),
    update=extend_schema(
        tags=["Menu Items"],
        summary="Replace a menu item",
        description="Available to platform admins and the owner of the item's restaurant.",
    ),
    partial_update=extend_schema(
        tags=["Menu Items"],
        summary="Update a menu item",
        description="Available to platform admins and the owner of the item's restaurant.",
    ),
    destroy=extend_schema(
        tags=["Menu Items"],
        summary="Delete a menu item",
        description="Available to platform admins and the owner of the item's restaurant.",
    ),
)
class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class=MenuItemSerializer
    permission_classes=[IsAuthenticated,MenuItemPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["menu", "category"]
    search_fields = ["name", "description", "category", "menu__name"]
    ordering_fields = ["id", "name", "category", "price", "created_at", "updated_at"]
    ordering = ["id"]

    def get_queryset(self):
        user=self.request.user
        queryset = MenuItem.objects.select_related("menu", "menu__restuarant")
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return queryset.order_by("name")
        elif user.role== User.RoleChoices.OWNER:
            return queryset.filter(menu__restuarant__owner=user).order_by("name")
        elif user.role in [User.RoleChoices.WAITER,User.RoleChoices.CHEF]:
            return queryset.filter(menu__restuarant=user.restaurant).order_by("name")
        return queryset.none()
