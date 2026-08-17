from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from menu.models import Menu
from menu.permissions import MenuPermission
from menuItem.models import MenuItem
from menuItem.permissions import MenuItemPermission
from order.models import Order
from order.permissions import OrderPermission
from restaurant.models import Restaurant
from restaurant.permissions import RestaurantPermission
from table.models import Table
from table.permissions import TablePermission
from user.models import User
from user.permissions import RolePermission


class RolePermissionTest(TestCase):
    password = "FocusedTests!2026-Strong"

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SimpleNamespace()

        self.admin = self.create_user(
            "admin@example.com",
            User.RoleChoices.PLATFORM_ADMIN,
        )
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
        self.other_waiter = self.create_user(
            "other-waiter@example.com",
            User.RoleChoices.WAITER,
            self.other_restaurant,
        )

        self.menu = Menu.objects.create(
            name="Owner Menu",
            description="Test menu",
            restuarant=self.restaurant,
        )
        self.other_menu = Menu.objects.create(
            name="Other Menu",
            description="Other menu",
            restuarant=self.other_restaurant,
        )
        self.menu_item = MenuItem.objects.create(
            name="Owner Item",
            category="Main",
            price="10.00",
            description="Test item",
            menu=self.menu,
        )
        self.other_menu_item = MenuItem.objects.create(
            name="Other Item",
            category="Main",
            price="12.00",
            description="Other item",
            menu=self.other_menu,
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
        self.order = Order.objects.create(
            restuarant=self.restaurant,
            table=self.table,
            waiter=self.waiter,
        )
        self.other_order = Order.objects.create(
            restuarant=self.other_restaurant,
            table=self.other_table,
            waiter=self.other_waiter,
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

    def request(self, method, user):
        request = getattr(self.factory, method.lower())("/")
        request.user = user
        return request

    def test_user_management_permission_is_scoped_to_owner_staff(self):
        permission = RolePermission()

        self.assertTrue(permission.has_permission(self.request("GET", self.admin), self.view))
        self.assertTrue(permission.has_permission(self.request("GET", self.owner), self.view))
        self.assertFalse(permission.has_permission(self.request("GET", self.waiter), self.view))
        self.assertTrue(
            permission.has_object_permission(
                self.request("PATCH", self.owner),
                self.view,
                self.waiter,
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("PATCH", self.owner),
                self.view,
                self.other_waiter,
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("PATCH", self.owner),
                self.view,
                self.other_owner,
            )
        )

    def test_restaurant_permission_matrix(self):
        permission = RestaurantPermission()

        self.assertTrue(permission.has_permission(self.request("POST", self.admin), self.view))
        self.assertFalse(permission.has_permission(self.request("POST", self.owner), self.view))
        self.assertTrue(permission.has_permission(self.request("PATCH", self.owner), self.view))
        self.assertTrue(permission.has_permission(self.request("GET", self.chef), self.view))
        self.assertFalse(permission.has_permission(self.request("PATCH", self.chef), self.view))
        self.assertTrue(
            permission.has_object_permission(
                self.request("PATCH", self.owner), self.view, self.restaurant
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("PATCH", self.owner), self.view, self.other_restaurant
            )
        )

    def test_menu_and_menu_item_permissions_are_restaurant_scoped(self):
        menu_permission = MenuPermission()
        item_permission = MenuItemPermission()

        self.assertTrue(
            menu_permission.has_object_permission(
                self.request("PATCH", self.owner), self.view, self.menu
            )
        )
        self.assertFalse(
            menu_permission.has_object_permission(
                self.request("PATCH", self.owner), self.view, self.other_menu
            )
        )
        self.assertTrue(
            item_permission.has_object_permission(
                self.request("GET", self.chef), self.view, self.menu_item
            )
        )
        self.assertFalse(
            item_permission.has_object_permission(
                self.request("GET", self.chef), self.view, self.other_menu_item
            )
        )
        self.assertFalse(
            item_permission.has_permission(
                self.request("POST", self.chef), self.view
            )
        )

    def test_table_permission_allows_staff_read_only_in_assigned_restaurant(self):
        permission = TablePermission()

        self.assertTrue(permission.has_permission(self.request("GET", self.waiter), self.view))
        self.assertTrue(permission.has_permission(self.request("GET", self.chef), self.view))
        self.assertFalse(permission.has_permission(self.request("PATCH", self.waiter), self.view))
        self.assertTrue(
            permission.has_object_permission(
                self.request("GET", self.waiter), self.view, self.table
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("GET", self.waiter), self.view, self.other_table
            )
        )

    def test_order_permission_matrix(self):
        permission = OrderPermission()

        self.assertTrue(permission.has_permission(self.request("POST", self.waiter), self.view))
        self.assertFalse(permission.has_permission(self.request("DELETE", self.waiter), self.view))
        self.assertTrue(permission.has_permission(self.request("PATCH", self.chef), self.view))
        self.assertFalse(permission.has_permission(self.request("POST", self.chef), self.view))
        self.assertTrue(
            permission.has_object_permission(
                self.request("PATCH", self.waiter), self.view, self.order
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("PATCH", self.waiter), self.view, self.other_order
            )
        )
        self.assertTrue(
            permission.has_object_permission(
                self.request("PATCH", self.chef), self.view, self.order
            )
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request("DELETE", self.chef), self.view, self.order
            )
        )
