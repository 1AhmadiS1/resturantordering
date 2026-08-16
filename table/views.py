from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from restaurant.models import Restaurant
from user.models import User

from .models import Table
from .permissions import TablePermission
from .serializer import TableSerializer


# Create your views here.
@extend_schema_view(
    list=extend_schema(tags=["Table"]),
    create=extend_schema(tags=["Table"]),
    retrieve=extend_schema(tags=["Table"]),
    update=extend_schema(tags=["Table"]),
    partial_update=extend_schema(tags=["Table"]),
    destroy=extend_schema(tags=["Table"]),
    
)
class TableView(ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, TablePermission)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restaurant", "table_number", "capacity", "status"]
    search_fields = ["restaurant__name"]
    ordering_fields = ["id", "table_number", "capacity", "status", "created_at", "updated_at"]
    ordering = ["table_number"]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return Table.objects.all().order_by("table_number")
        if user.role == User.RoleChoices.OWNER:
            return Table.objects.filter(restaurant__owner=user).order_by("table_number")
        if user.role == User.RoleChoices.WAITER:
            return Table.objects.filter(restaurant=user.restaurant).order_by("table_number")
        return Table.objects.none()
