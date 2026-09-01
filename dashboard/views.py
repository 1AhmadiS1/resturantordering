
from django.db.models import Count, Sum
from django.utils import timezone 

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User
from restaurant.models import Restaurant
from order.models import Order
from table.models import Table
from menuItem.models import MenuItem
from .serializers import DashboardSerializer
# Create your views here.

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Get dashboard overview",
        description="Returns dashboard data for platform admins and restaurant owners.",
        responses=DashboardSerializer,
    )
    def get(self,request):
        user=request.user
        restaurants=self.get_restaurants(user)
        today=timezone.now().date()
        
        
        if restaurants is None:
            return Response({"detail": "Not allowed"}, status=403)
        # Active order
        active_orders = Order.objects.filter(
        status__in=[
            Order.StatusChoices.PREPARING,
            Order.StatusChoices.PENDING,
            Order.StatusChoices.READY,
        ],
        restuarant__in=restaurants
        ).count()
        
        
           
        today_orders=Order.objects.filter(restuarant__in=restaurants,created_at__date=today).count()
    
        today_revenue = Order.objects.filter(
            restuarant__in=restaurants,
            created_at__date=today,
            status=Order.StatusChoices.SERVED,
        ).aggregate(total=Sum("total_price"))["total"] or 0
        available_tables =Table.objects.filter(restaurant__in=restaurants,
        status=Table.StatusChoices.AVAILABLE
        ).count()
        total_tables =Table.objects.filter(restaurant__in=restaurants).count()
        menu_items_count=MenuItem.objects.filter(menu__restuarant__in=restaurants).count()
        staff_count = User.objects.filter(restaurant__in=restaurants).count()
        

        summary = {
            "active_orders": active_orders,
            "today_orders": today_orders,
            "today_revenue": today_revenue,
            "available_tables": available_tables,
            "total_tables": total_tables,
            "menu_items_count": menu_items_count,
            "staff_count": staff_count,
        }


        # kitchen pulse
        pending=Order.objects.filter(restuarant__in=restaurants,
        status=Order.StatusChoices.PENDING
        ).count()
        preparing=Order.objects.filter(restuarant__in=restaurants,
        status=Order.StatusChoices.PREPARING
        ).count()
        ready=Order.objects.filter(restuarant__in=restaurants,
        status=Order.StatusChoices.READY
        ).count()
        
        kitchen_pulse ={
            "pending":pending,
            "preparing":preparing,
            "ready":ready
        }

        # recent orders
        recent_orders = (
            Order.objects.filter(restuarant__in=restaurants)
            .select_related("table")
            .annotate(items_count=Count("order_items"))
            .order_by("-created_at")[:5]
        )

        recent_orders_data = [
            {
                "id": order.id,
                "table_number": order.table.table_number,
                "items_count": order.items_count,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": order.created_at,
            }
            for order in recent_orders
        ]

        # popular items
        popular_items = (
            MenuItem.objects.filter(menu__restuarant__in=restaurants)
            .annotate(orders_count=Sum("order_items__quantity"))
            .order_by("-orders_count")[:5]
        )
        popular_items_data = []

        for item in popular_items:
            item_data = {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "image": item.image.url if item.image else None,
                "orders_count": item.orders_count or 0,
            }

            popular_items_data.append(item_data)
        data = {
            "summary": summary,
            "recent_orders": recent_orders_data,
            "popular_items": popular_items_data,
            "kitchen_pulse": kitchen_pulse,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data) 

    def get_restaurants(self, user):
        restaurant_id = self.request.query_params.get("restaurant")

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            restaurants = Restaurant.objects.all()

        elif user.role == User.RoleChoices.OWNER:
            restaurants = Restaurant.objects.filter(owner=user)

        else:
            return None

        if restaurant_id:
            restaurants = restaurants.filter(id=restaurant_id)

        return restaurants

