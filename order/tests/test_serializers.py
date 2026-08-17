from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase

from menu.models import Menu
from menuItem.models import MenuItem
from order.models import Order, OrderItem
from order.serializer import OrderSerializer
from restaurant.models import Restaurant
from table.models import Table
from user.models import User


class OrderSerializerTest(TestCase):
    password = "FocusedTests!2026-Strong"

    def setUp(self):
        self.owner = self.create_user("owner@example.com", User.RoleChoices.OWNER)
        self.other_owner = self.create_user(
            "other-owner@example.com",
            User.RoleChoices.OWNER,
        )
        self.restaurant = self.create_restaurant(
            "Owner Restaurant",
            "owner-restaurant@example.com",
            self.owner,
        )
        self.other_restaurant = self.create_restaurant(
            "Other Restaurant",
            "other-restaurant@example.com",
            self.other_owner,
        )
        self.waiter = self.create_user(
            "waiter@example.com",
            User.RoleChoices.WAITER,
            self.restaurant,
        )
        self.chef = self.create_user(
            "chef@example.com",
            User.RoleChoices.CHEF,
            self.restaurant,
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number=1,
            capacity=4,
        )
        self.other_table = Table.objects.create(
            restaurant=self.other_restaurant,
            table_number=1,
            capacity=4,
        )
        self.menu = Menu.objects.create(
            name="Owner Menu",
            description="Test menu",
            restuarant=self.restaurant,
        )
        self.other_menu = Menu.objects.create(
            name="Other Menu",
            description="Other test menu",
            restuarant=self.other_restaurant,
        )
        self.burger = self.create_menu_item(
            "Burger",
            Decimal("12.50"),
            self.menu,
        )
        self.drink = self.create_menu_item(
            "Drink",
            Decimal("6.75"),
            self.menu,
        )
        self.foreign_item = self.create_menu_item(
            "Foreign Item",
            Decimal("20.00"),
            self.other_menu,
        )

    def create_user(self, email, role, restaurant=None):
        return User.objects.create_user(
            email=email,
            password=self.password,
            first_name="Test",
            last_name=role,
            role=role,
            restaurant=restaurant,
        )

    def create_restaurant(self, name, email, owner):
        return Restaurant.objects.create(
            name=name,
            owner=owner,
            address="Test Address",
            phone="123456789",
            email=email,
            description="Test restaurant",
        )

    def create_menu_item(self, name, price, menu):
        return MenuItem.objects.create(
            name=name,
            category="Main",
            price=price,
            description="Test item",
            menu=menu,
        )

    def request_for(self, user):
        return SimpleNamespace(user=user)

    def create_order(self, status=Order.StatusChoices.PENDING):
        order = Order.objects.create(
            restuarant=self.restaurant,
            table=self.table,
            waiter=self.waiter,
            status=status,
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.burger,
            quantity=1,
            price=self.burger.price,
        )
        order.total_price = self.burger.price
        order.save(update_fields=["total_price"])
        return order

    def serializer_for_update(self, order, user, data):
        return OrderSerializer(
            instance=order,
            data=data,
            partial=True,
            context={"request": self.request_for(user)},
        )

    def test_create_calculates_total_and_assigns_waiter(self):
        serializer = OrderSerializer(
            data={
                "table": self.table.id,
                "note": "Focused serializer test",
                "items": [
                    {"menu_item": self.burger.id, "quantity": 2},
                    {"menu_item": self.drink.id, "quantity": 1},
                ],
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.assertEqual(order.restuarant, self.restaurant)
        self.assertEqual(order.waiter, self.waiter)
        self.assertEqual(order.status, Order.StatusChoices.PENDING)
        self.assertEqual(order.total_price, Decimal("31.75"))
        self.assertEqual(order.order_items.count(), 2)
        self.assertEqual(
            order.order_items.get(menu_item=self.burger).price,
            self.burger.price,
        )

    def test_create_rejects_item_from_another_restaurant(self):
        serializer = OrderSerializer(
            data={
                "table": self.table.id,
                "items": [{"menu_item": self.foreign_item.id, "quantity": 1}],
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_rejects_duplicate_menu_items(self):
        serializer = OrderSerializer(
            data={
                "table": self.table.id,
                "items": [
                    {"menu_item": self.burger.id, "quantity": 1},
                    {"menu_item": self.burger.id, "quantity": 2},
                ],
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_create_rejects_non_positive_quantity(self):
        serializer = OrderSerializer(
            data={
                "table": self.table.id,
                "items": [{"menu_item": self.burger.id, "quantity": 0}],
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_owner_cannot_create_order_for_another_restaurant(self):
        serializer = OrderSerializer(
            data={
                "table": self.other_table.id,
                "items": [{"menu_item": self.foreign_item.id, "quantity": 1}],
            },
            context={"request": self.request_for(self.owner)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("table", serializer.errors)

    def test_replacing_items_recalculates_total_and_resets_status(self):
        order = self.create_order(status=Order.StatusChoices.READY)
        serializer = self.serializer_for_update(
            order,
            self.owner,
            {"items": [{"menu_item": self.drink.id, "quantity": 3}]},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        order.refresh_from_db()

        self.assertEqual(order.status, Order.StatusChoices.PENDING)
        self.assertEqual(order.total_price, Decimal("20.25"))
        self.assertEqual(order.order_items.count(), 1)
        item = order.order_items.get()
        self.assertEqual(item.menu_item, self.drink)
        self.assertEqual(item.quantity, 3)

    def test_table_cannot_be_changed_after_creation(self):
        second_table = Table.objects.create(
            restaurant=self.restaurant,
            table_number=2,
            capacity=2,
        )
        order = self.create_order()
        serializer = self.serializer_for_update(
            order,
            self.owner,
            {"table": second_table.id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("table", serializer.errors)

    def test_chef_status_transitions(self):
        pending_order = self.create_order()
        preparing_serializer = self.serializer_for_update(
            pending_order,
            self.chef,
            {"status": Order.StatusChoices.PREPARING},
        )
        self.assertTrue(preparing_serializer.is_valid(), preparing_serializer.errors)
        preparing_order = preparing_serializer.save()

        ready_serializer = self.serializer_for_update(
            preparing_order,
            self.chef,
            {"status": Order.StatusChoices.READY},
        )
        self.assertTrue(ready_serializer.is_valid(), ready_serializer.errors)
        ready_order = ready_serializer.save()
        self.assertEqual(ready_order.status, Order.StatusChoices.READY)

        forbidden_order = self.create_order()
        forbidden_serializer = self.serializer_for_update(
            forbidden_order,
            self.chef,
            {"status": Order.StatusChoices.CANCELLED},
        )
        self.assertFalse(forbidden_serializer.is_valid())
        self.assertIn("status", forbidden_serializer.errors)

    def test_waiter_status_transitions(self):
        ready_order = self.create_order(status=Order.StatusChoices.READY)
        served_serializer = self.serializer_for_update(
            ready_order,
            self.waiter,
            {"status": Order.StatusChoices.SERVED},
        )
        self.assertTrue(served_serializer.is_valid(), served_serializer.errors)
        served_order = served_serializer.save()
        self.assertEqual(served_order.status, Order.StatusChoices.SERVED)

        pending_order = self.create_order()
        forbidden_serializer = self.serializer_for_update(
            pending_order,
            self.waiter,
            {"status": Order.StatusChoices.PREPARING},
        )
        self.assertFalse(forbidden_serializer.is_valid())
        self.assertIn("status", forbidden_serializer.errors)

    def test_terminal_order_cannot_be_changed(self):
        order = self.create_order(status=Order.StatusChoices.SERVED)
        serializer = self.serializer_for_update(
            order,
            self.owner,
            {"note": "Forbidden change"},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
