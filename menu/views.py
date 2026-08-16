from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from menu.permissions import MenuPermission
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render
from rest_framework import viewsets
from .models import Menu
from .serializer import MenuSerializer
from user.models import User
# Create your views here.
@extend_schema_view(
    list=extend_schema(tags=["Menu"]),
    retrieve=extend_schema(tags=["Menu"]),
    create=extend_schema(tags=["Menu"]),
    update=extend_schema(tags=["Menu"]),
    partial_update=extend_schema(tags=["Menu"]),
    destroy=extend_schema(tags=["Menu"]),
)
class MenuModelViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, MenuPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["restuarant"]
    search_fields = ["name", "description", "restuarant__name"]
    ordering_fields = ["id", "name", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        user=self.request.user
        if user.role == User.RoleChoices.OWNER:
            return Menu.objects.filter(restuarant__owner=user).order_by("name")
        elif user.role in [User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return Menu.objects.filter(restuarant=user.restaurant).order_by("name")
        elif user.role == User.RoleChoices.PLATFORM_ADMIN:
            return Menu.objects.all().order_by("name")
        return Menu.objects.none()    
    
