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
    list=extend_schema(
        tags=["Orders"],
        summary="List visible orders",
        description=(
            "Platform admins see every order, owners see orders for their restaurants, "
            "and waiters or chefs see orders for their assigned restaurant."
        ),
    ),
    retrieve=extend_schema(
        tags=["Orders"],
        summary="Get an order",
        description="Return one order, including readable restaurant, table, waiter, and item details.",
    ),
    create=extend_schema(
        tags=["Orders"],
        summary="Create an order with items",
        description=(
            "Available to platform admins, owners, and waiters. Send a table ID and at least "
            "one item. The restaurant, waiter, item prices, total price, and pending status "
            "are controlled by the server."
        ),
    ),
    update=extend_schema(
        tags=["Orders"],
        summary="Replace an order",
        description=(
            "Replace editable order data. Replacing items recalculates the total and resets "
            "the order status to pending. Chefs cannot use this operation."
        ),
    ),
    partial_update=extend_schema(
        tags=["Orders"],
        summary="Update an order or its status",
        description=(
            "Waiters manage pending items and mark ready orders served. Chefs move pending "
            "orders to preparing and preparing orders to ready. Owners and platform admins "
            "may perform any valid forward transition or cancel an active order."
        ),
    ),
    destroy=extend_schema(
        tags=["Orders"],
        summary="Delete an order",
        description="Available only to platform admins and the owner of the order's restaurant.",
    ),
)
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restuarant", "table", "waiter", "status"]
    search_fields = ["note", "restuarant__name", "waiter__email"]
    ordering_fields = ["id", "total_price", "status", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related(
            "restuarant",
            "table",
            "waiter",
        ).prefetch_related("order_items__menu_item")

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return queryset

        if user.role == User.RoleChoices.OWNER:
            return queryset.filter(restuarant__owner=user)

        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return queryset.filter(restuarant=user.restaurant)

        return queryset.none()
