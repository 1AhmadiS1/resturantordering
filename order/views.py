from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

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

    def get_queryset(self):
        user = self.request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return Order.objects.all()

        if user.role == User.RoleChoices.OWNER:
            return Order.objects.filter(restuarant__owner=user)

        if user.role in [User.RoleChoices.WAITER, User.RoleChoices.CHEF]:
            return Order.objects.filter(restuarant=user.restaurant)

        return Order.objects.none()
