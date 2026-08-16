from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from user.models import User
from .models import Order
from .permissions import OrderPermission
from .serializer import OrderSerializer


@extend_schema_view(
    list=extend_schema(tags=["Orders"]),
    retrieve=extend_schema(tags=["Orders"]),
    create=extend_schema(tags=["Orders"]),
    update=extend_schema(tags=["Orders"]),
    partial_update=extend_schema(tags=["Orders"]),
    destroy=extend_schema(tags=["Orders"]),
)
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restuarant", "table", "waiter", "status"]
    search_fields = ["note", "restuarant__name", "waiter__email"]
    ordering_fields = ["id", "total_price", "status", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return Order.objects.all().order_by("created_at")

        if user.role == User.RoleChoices.OWNER:
            return Order.objects.filter(restuarant__owner=user).order_by("created_at")

        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return Order.objects.filter(restuarant=user.restaurant).order_by("created_at")

        return Order.objects.none()
