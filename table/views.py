from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from user.models import User

from .models import Table
from .permissions import TablePermission
from .serializer import TableSerializer


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=["Tables"],
        summary="List visible tables",
        description=(
            "Platform admins see all tables, owners see tables in their restaurants, and "
            "waiters or chefs see tables in their assigned restaurant."
        ),
    ),
    create=extend_schema(
        tags=["Tables"],
        summary="Create a table",
        description="Available to platform admins and restaurant owners. Table number and capacity must be at least 1.",
    ),
    retrieve=extend_schema(
        tags=["Tables"],
        summary="Get a table",
        description="Return one visible table with readable restaurant and status values.",
    ),
    update=extend_schema(
        tags=["Tables"],
        summary="Replace a table",
        description="Available to platform admins and the owner of the table's restaurant.",
    ),
    partial_update=extend_schema(
        tags=["Tables"],
        summary="Update a table",
        description="Available to platform admins and the owner of the table's restaurant.",
    ),
    destroy=extend_schema(
        tags=["Tables"],
        summary="Delete a table",
        description="Available to platform admins and the owner of the table's restaurant.",
    ),
)
class TableView(ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, TablePermission)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restaurant", "table_number", "capacity", "status"]
    search_fields = ["restaurant__name"]
    ordering_fields = ["id", "table_number", "capacity", "status", "created_at", "updated_at"]
    ordering = ["table_number"]

    def get_queryset(self):
        user = self.request.user
        queryset = Table.objects.select_related("restaurant")
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return queryset.order_by("table_number")
        if user.role == User.RoleChoices.OWNER:
            return queryset.filter(restaurant__owner=user).order_by("table_number")
        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return queryset.filter(restaurant=user.restaurant).order_by("table_number")
        return queryset.none()
