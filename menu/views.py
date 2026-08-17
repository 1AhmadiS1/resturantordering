from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from menu.permissions import MenuPermission
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets
from .models import Menu
from .serializer import MenuSerializer
from user.models import User
# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=["Menus"],
        summary="List visible menus",
        description="Return menus belonging to restaurants visible to the authenticated user.",
    ),
    retrieve=extend_schema(
        tags=["Menus"],
        summary="Get a menu",
        description="Return one visible menu with its restaurant name.",
    ),
    create=extend_schema(
        tags=["Menus"],
        summary="Create a menu",
        description=(
            "Platform admins may create a menu for any restaurant. Owners may create one "
            "only for a restaurant they own. Each restaurant supports one menu."
        ),
    ),
    update=extend_schema(
        tags=["Menus"],
        summary="Replace a menu",
        description="Available to platform admins and the owner of the menu's restaurant.",
    ),
    partial_update=extend_schema(
        tags=["Menus"],
        summary="Update a menu",
        description="Available to platform admins and the owner of the menu's restaurant.",
    ),
    destroy=extend_schema(
        tags=["Menus"],
        summary="Delete a menu",
        description="Available to platform admins and the owner of the menu's restaurant.",
    ),
)
class MenuModelViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, MenuPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restuarant"]
    search_fields = ["name", "description", "restuarant__name"]
    ordering_fields = ["id", "name", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        user=self.request.user
        queryset = Menu.objects.select_related("restuarant")
        if user.role == User.RoleChoices.OWNER:
            return queryset.filter(restuarant__owner=user).order_by("name")
        elif user.role in [User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return queryset.filter(restuarant=user.restaurant).order_by("name")
        elif user.role == User.RoleChoices.PLATFORM_ADMIN:
            return queryset.order_by("name")
        return queryset.none()
