from decimal import Decimal

from django.test import TestCase

from menu.models import Menu
from menuItem.models import MenuItem
from order.models import Order, OrderItem
from restaurant.models import Restaurant
from table.models import Table
from user.models import User


class OrderModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="model-owner@example.com",
            password="FocusedTests!2026-Strong",
            first_name="Model",
            last_name="Owner",
            role=User.RoleChoices.OWNER,
        )
        self.restaurant = Restaurant.objects.create(
            name="Model Restaurant",
            owner=self.owner,
            address="123 Main Street",
            phone="1234567890",
            email="model-restaurant@example.com",
            description="Restaurant used by model tests.",
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number=1,
            capacity=4,
        )
        self.menu = Menu.objects.create(
            name="Model Menu",
            description="Menu used by model tests.",
            restuarant=self.restaurant,
        )
        self.menu_item = MenuItem.objects.create(
            name="Model Burger",
            category="Main",
            price=Decimal("10.50"),
            description="Item used by model tests.",
            menu=self.menu,
        )
        self.order = Order.objects.create(
            restuarant=self.restaurant,
            table=self.table,
        )

    def test_order_defaults_and_relationships(self):
        self.assertEqual(self.order.status, Order.StatusChoices.PENDING)
        self.assertEqual(self.order.total_price, 0)
        self.assertIsNone(self.order.waiter)
        self.assertEqual(self.order.restuarant, self.restaurant)
        self.assertEqual(self.order.table, self.table)
        self.assertEqual(str(self.order), f"Order {self.order.id}")

    def test_order_item_relationship_and_price_snapshot(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2,
            price=self.menu_item.price,
        )

        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.menu_item, self.menu_item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("10.50"))
        self.assertEqual(self.order.order_items.get(), order_item)
