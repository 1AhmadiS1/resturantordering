from drf_spectacular.utils import extend_schema_view
from drf_spectacular.utils import extend_schema
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Restaurant
from .serializer import ResturantSerializer
from user.models import User
from .permissions import RestaurantPermission

# Create your views here.
@extend_schema_view(
    list=extend_schema(tags=["Restaurants"]),
    retrieve=extend_schema(tags=["Restaurants"]),
    create=extend_schema(tags=["Restaurants"]),
    update=extend_schema(tags=["Restaurants"]),
    partial_update=extend_schema(tags=["Restaurants"]),
    destroy=extend_schema(tags=["Restaurants"]),
)
class RestaurantView(viewsets.ModelViewSet):
    serializer_class = ResturantSerializer
    permission_classes=[IsAuthenticated,RestaurantPermission]    
    def get_queryset(self):
        user=self.request.user
        if user.role==User.RoleChoices.PLATFORM_ADMIN:
            return Restaurant.objects.all()
        elif user.role == User.RoleChoices.OWNER:
            return Restaurant.objects.filter(owner=user)  
        elif user.role in [User.RoleChoices.CHEF,User.RoleChoices.WAITER]:
            return Restaurant.objects.filter(employees=user)
        else:
            return Restaurant.objects.none()          
        
