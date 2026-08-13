from user.models import User
from .models import Order,OrderItem
from rest_framework import serializers


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menu_item", "quantity", "price", "created_at", "updated_at"]
        read_only_fields = ["price", "id", "created_at", "updated_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        menu_item = attrs.get("menu_item")
        order = attrs.get("order")
        quantity = attrs.get("quantity", 1)

        if menu_item.menu.restuarant != order.restuarant:
            raise serializers.ValidationError(
                "Menu item must be from the same restuarant as the order."
            )

        if user.role == User.RoleChoices.OWNER:
            if order.restuarant.owner != user:
                raise serializers.ValidationError(
                    "You can only add items to orders from your own restuarant."
                )

        elif user.role == User.RoleChoices.WAITER:
            if order.restuarant != user.restaurant:
                raise serializers.ValidationError(
                    "You can only add items to orders from your assigned restuarant."
                )

        elif user.role == User.RoleChoices.PLATFORM_ADMIN:
            pass

        else:
            raise serializers.ValidationError("Invalid user role.")

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")

        return attrs

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "price", "created_at", "updated_at"]
        read_only_fields = ["price", "id", "created_at", "updated_at"]



class OrderSerializer(serializers.ModelSerializer):

    items=OrderItemCreateSerializer(many=True,source="order_items")

    class Meta:
        model=Order
        fields=["id","table","restuarant","waiter","total_price","status","note","created_at","updated_at","items"]
        read_only_fields=["total_price","restuarant","created_at","updated_at","waiter","id"]
    def validate(self,attrs):
        menu_items=attrs.get("menu_items")
        user=self.context["request"].user
        table=attrs.get("table")
    
        if user.role == User.RoleChoices.WAITER:
            if table.restaurant != user.restaurant:
                raise serializers.ValidationError(
                    "You can only add items to orders from your assigned restuarant."
                )
        elif user.role == User.RoleChoices.PLATFORM_ADMIN:
            pass
        elif user.role == User.RoleChoices.OWNER:
            if table.restaurant.owner != user:
                raise serializers.ValidationError(
                    "You can only add items to orders from your own restuarant."
                )
        else:
            raise serializers.ValidationError("Invalid user role.")
        return attrs
    def validate_items(self,value):
        user=self.context["request"].user
        for item in value:
            if item.menu_item.menu.restuarant.owner != user:
                raise serializers.ValidationError(
                    "You can only add items to orders from your own restuarant."
                )
        return value
        
    def create(self,validated_data):
        items=validated_data.pop("order_items")
        table = validated_data["table"]
        order=Order.objects.create(restuarant=table.restaurant, waiter=self.context["request"].user, **validated_data)
        for item in items:
            menu_item = item["menu_item"]
            quantity = item.get("quantity", 1)
            if menu_item.menu.restuarant != table.restaurant:
                raise serializers.ValidationError(
                    "Menu item must be from the same restaurant as the order table."
                )
            price = menu_item.price
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity, price=price)
            order.total_price += price * quantity
        order.save()
        return order
            
# if we update items the status will be pending again


