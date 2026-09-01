from rest_framework import serializers

class DashboardSummarySerializer(serializers.Serializer):
    active_orders=serializers.IntegerField(read_only=True)
    today_orders=serializers.IntegerField(read_only=True)
    today_revenue=serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    available_tables=serializers.IntegerField(read_only=True)
    total_tables=serializers.IntegerField(read_only=True)
    menu_items_count=serializers.IntegerField(read_only=True)
    staff_count=serializers.IntegerField(read_only=True)

    
class RecentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    table_number = serializers.IntegerField()
    items_count = serializers.IntegerField()
    status = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()

    

class PopularItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.URLField(allow_null=True)
    orders_count = serializers.IntegerField()


class KitchenPulseSerializer(serializers.Serializer):
    pending = serializers.IntegerField()
    preparing = serializers.IntegerField()
    ready = serializers.IntegerField()
    

class DashboardSerializer(serializers.Serializer):
    summary = DashboardSummarySerializer()
    recent_orders = RecentOrderSerializer(many=True)
    popular_items = PopularItemSerializer(many=True)
    kitchen_pulse = KitchenPulseSerializer()
