from drf_spectacular.utils import extend_schema_view
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Restaurant
from .serializer import ResturantSerializer
from user.models import User
from .permissions import RestaurantPermission

# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=["Restaurants"],
        summary="List visible restaurants",
        description=(
            "Platform admins see all restaurants, owners see their restaurants, and staff "
            "see the restaurant to which they are assigned."
        ),
    ),
    retrieve=extend_schema(
        tags=["Restaurants"],
        summary="Get a restaurant",
        description="Return one restaurant visible to the authenticated user.",
    ),
    create=extend_schema(
        tags=["Restaurants"],
        summary="Create a restaurant",
        description="Only platform admins can create a restaurant and assign an owner.",
    ),
    update=extend_schema(
        tags=["Restaurants"],
        summary="Replace a restaurant",
        description="Platform admins may replace any restaurant; owners may replace only their own.",
    ),
    partial_update=extend_schema(
        tags=["Restaurants"],
        summary="Update a restaurant",
        description=(
            "Platform admins may update any restaurant. Owners may update their own, but "
            "only a platform admin can transfer ownership."
        ),
    ),
    destroy=extend_schema(
        tags=["Restaurants"],
        summary="Delete a restaurant",
        description="Available to platform admins and the restaurant's owner.",
    ),
)
class RestaurantView(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = ResturantSerializer
    permission_classes=[IsAuthenticated,RestaurantPermission]    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["owner"]
    search_fields = ["name", "address", "phone", "email"]
    ordering_fields = ["id", "name", "created_at", "updated_at"]
    ordering = ["id"]

    def get_queryset(self):
        user=self.request.user
        queryset = Restaurant.objects.select_related("owner")
        if user.role==User.RoleChoices.PLATFORM_ADMIN:
            return queryset.order_by("name")
        elif user.role == User.RoleChoices.OWNER:
            return queryset.filter(owner=user).order_by("name")
        elif user.role in [User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return queryset.filter(employees=user).order_by("name")
        else:
            return queryset.none()
