from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from resturantorderingapi.validators import validate_no_html
from user.models import User

from .models import Order, OrderItem


ALLOWED_STATUS_TRANSITIONS = {
    Order.StatusChoices.PENDING: {
        Order.StatusChoices.PREPARING,
        Order.StatusChoices.CANCELLED,
    },
    Order.StatusChoices.PREPARING: {
        Order.StatusChoices.READY,
        Order.StatusChoices.CANCELLED,
    },
    Order.StatusChoices.READY: {
        Order.StatusChoices.SERVED,
        Order.StatusChoices.CANCELLED,
    },
    Order.StatusChoices.SERVED: set(),
    Order.StatusChoices.CANCELLED: set(),
}

ROLE_STATUS_TRANSITIONS = {
    User.RoleChoices.WAITER: {
        (Order.StatusChoices.PENDING, Order.StatusChoices.CANCELLED),
        (Order.StatusChoices.READY, Order.StatusChoices.SERVED),
    },
    User.RoleChoices.CHEF: {
        (Order.StatusChoices.PENDING, Order.StatusChoices.PREPARING),
        (Order.StatusChoices.PREPARING, Order.StatusChoices.READY),
    },
}


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "menu_item",
            "menu_item_name",
            "quantity",
            "price",
            "line_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "price",
            "menu_item_name",
            "line_total",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_line_total(self, obj):
        return obj.price * obj.quantity

    def validate(self, attrs):
        user = self.context["request"].user
        menu_item = attrs.get("menu_item", getattr(self.instance, "menu_item", None))
        order = attrs.get("order", getattr(self.instance, "order", None))

        if menu_item and order and menu_item.menu.restuarant_id != order.restuarant_id:
            raise serializers.ValidationError(
                {"menu_item": "Menu item must be from the same restaurant as the order."}
            )

        if order:
            if user.role == User.RoleChoices.OWNER and order.restuarant.owner_id != user.id:
                raise serializers.ValidationError(
                    "You can only manage items for orders from your own restaurant."
                )

            if user.role == User.RoleChoices.WAITER and order.restuarant_id != user.restaurant_id:
                raise serializers.ValidationError(
                    "You can only manage items for orders from your assigned restaurant."
                )

        if user.role not in {
            User.RoleChoices.PLATFORM_ADMIN,
            User.RoleChoices.OWNER,
            User.RoleChoices.WAITER,
        }:
            raise serializers.ValidationError("Your role cannot manage order items.")

        return attrs


class OrderItemCreateSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_name",
            "quantity",
            "price",
            "line_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "price",
            "menu_item_name",
            "line_total",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_line_total(self, obj):
        return obj.price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, source="order_items")
    table_number = serializers.IntegerField(source="table.table_number", read_only=True)
    restaurant_name = serializers.CharField(source="restuarant.name", read_only=True)
    waiter_email = serializers.EmailField(
        source="waiter.email",
        read_only=True,
        allow_null=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "table_number",
            "restuarant",
            "restaurant_name",
            "waiter",
            "waiter_email",
            "total_price",
            "status",
            "status_display",
            "note",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "restuarant",
            "restaurant_name",
            "table_number",
            "waiter",
            "waiter_email",
            "total_price",
            "status_display",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "table": {
                "help_text": "Table ID. The order restaurant is taken from this table."
            },
            "status": {
                "help_text": (
                    "Order flow: pending -> preparing -> ready -> served. "
                    "Pending, preparing, or ready orders may also be cancelled."
                )
            },
        }

    def validate_note(self, value):
        return validate_no_html(value)

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        table = attrs.get("table", getattr(self.instance, "table", None))
        items = attrs.get("order_items")

        if self.instance and "table" in attrs and table != self.instance.table:
            raise serializers.ValidationError(
                {"table": "The table cannot be changed after an order is created."}
            )

        if table is not None:
            self._validate_restaurant_access(user, table.restaurant)

        if self.instance is None:
            if not items:
                raise serializers.ValidationError(
                    {"items": "An order must contain at least one item."}
                )
        elif items is not None:
            if not items:
                raise serializers.ValidationError(
                    {"items": "An order must contain at least one item."}
                )
            if self.instance.status in {
                Order.StatusChoices.SERVED,
                Order.StatusChoices.CANCELLED,
            }:
                raise serializers.ValidationError(
                    {"items": "Items cannot be changed on a served or cancelled order."}
                )

        if items is not None and table is not None:
            self._validate_items(items, table.restaurant_id)

        self._validate_update_fields(user, attrs)
        self._validate_status(user, attrs, items)
        return attrs

    def _validate_restaurant_access(self, user, restaurant):
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return

        if user.role == User.RoleChoices.OWNER:
            if restaurant.owner_id != user.id:
                raise serializers.ValidationError(
                    {"table": "You can only manage orders for your own restaurant."}
                )
            return

        if user.role in {User.RoleChoices.WAITER, User.RoleChoices.CHEF}:
            if restaurant.id != user.restaurant_id:
                raise serializers.ValidationError(
                    {"table": "You can only manage orders for your assigned restaurant."}
                )
            return

        raise serializers.ValidationError("Your role cannot manage orders.")

    def _validate_items(self, items, restaurant_id):
        menu_item_ids = []

        for item in items:
            menu_item = item["menu_item"]
            menu_item_ids.append(menu_item.id)
            if menu_item.menu.restuarant_id != restaurant_id:
                raise serializers.ValidationError(
                    {
                        "items": (
                            f"Menu item {menu_item.id} is not from the same restaurant "
                            "as the order table."
                        )
                    }
                )

        if len(menu_item_ids) != len(set(menu_item_ids)):
            raise serializers.ValidationError(
                {"items": "Each menu item may appear only once; use quantity instead."}
            )

    def _validate_update_fields(self, user, attrs):
        if self.instance is None:
            if user.role == User.RoleChoices.CHEF:
                raise serializers.ValidationError("Chefs cannot create orders.")
            return

        if self.instance.status in {
            Order.StatusChoices.SERVED,
            Order.StatusChoices.CANCELLED,
        } and attrs:
            raise serializers.ValidationError(
                "Served and cancelled orders cannot be changed."
            )

        if user.role == User.RoleChoices.CHEF:
            disallowed_fields = set(attrs) - {"status"}
            if disallowed_fields:
                raise serializers.ValidationError(
                    "Chefs may only update an order's status."
                )

    def _validate_status(self, user, attrs, items):
        new_status = attrs.get("status")

        if self.instance is None:
            if new_status and new_status != Order.StatusChoices.PENDING:
                raise serializers.ValidationError(
                    {"status": "New orders must start with pending status."}
                )
            return

        if items is not None:
            if new_status and new_status != Order.StatusChoices.PENDING:
                raise serializers.ValidationError(
                    {"status": "Changing order items resets the status to pending."}
                )
            return

        old_status = self.instance.status
        if not new_status or new_status == old_status:
            return

        if new_status not in ALLOWED_STATUS_TRANSITIONS.get(old_status, set()):
            raise serializers.ValidationError(
                {"status": f"Status cannot change from {old_status} to {new_status}."}
            )

        if user.role in ROLE_STATUS_TRANSITIONS:
            transition = (old_status, new_status)
            if transition not in ROLE_STATUS_TRANSITIONS[user.role]:
                if user.role == User.RoleChoices.CHEF:
                    message = "Chefs may only move pending to preparing, or preparing to ready."
                else:
                    message = "Waiters may only cancel pending orders or mark ready orders served."
                raise serializers.ValidationError({"status": message})

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("order_items")
        table = validated_data["table"]
        user = self.context["request"].user
        waiter = user if user.role == User.RoleChoices.WAITER else None
        order = Order.objects.create(
            restuarant=table.restaurant,
            waiter=waiter,
            **validated_data,
        )
        order.total_price = self._create_order_items(order, items)
        order.save(update_fields=["total_price", "updated_at"])
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        missing = object()
        items = validated_data.pop("order_items", missing)
        order = super().update(instance, validated_data)

        if items is not missing:
            order.order_items.all().delete()
            order.total_price = self._create_order_items(order, items)
            order.status = Order.StatusChoices.PENDING
            order.save(update_fields=["total_price", "status", "updated_at"])

        return order

    def _create_order_items(self, order, items):
        total_price = Decimal("0.00")

        for item in items:
            menu_item = item["menu_item"]
            quantity = item.get("quantity", 1)
            price = menu_item.price
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price,
            )
            total_price += price * quantity

        return total_price
