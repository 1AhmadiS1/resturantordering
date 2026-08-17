from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from order.models import Order
from user.models import User


class SwaggerApiWorkflowTest(APITestCase):
    password = "Testing-API!2026xZ"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="swagger-admin@example.com",
            password=self.password,
            first_name="Swagger",
            last_name="Admin",
        )

    def authenticate(self, email):
        response = self.client.post(
            "/api/token/",
            {"email": email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        return response.data

    def create_user(self, email, role, restaurant=None):
        payload = {
            "email": email,
            "password": self.password,
            "first_name": "Swagger",
            "last_name": role.title(),
            "role": role,
            "restaurant": restaurant,
        }
        response = self.client.post("/api/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertNotIn("password", response.data)
        return response.data

    def test_complete_swagger_workflow(self):
        self.authenticate(self.admin.email)

        owner = self.create_user(
            "swagger-owner@example.com",
            User.RoleChoices.OWNER,
        )

        restaurant_response = self.client.post(
            "/api/restaurants/",
            {
                "name": "Swagger Kitchen",
                "owner": owner["id"],
                "address": "1 API Street",
                "phone": "+970599000001",
                "email": "swagger-kitchen@example.com",
                "description": "Restaurant created by the API workflow test.",
            },
            format="json",
        )
        self.assertEqual(
            restaurant_response.status_code,
            status.HTTP_201_CREATED,
            restaurant_response.data,
        )
        restaurant = restaurant_response.data
        self.assertEqual(restaurant["owner_email"], owner["email"])

        waiter = self.create_user(
            "swagger-waiter@example.com",
            User.RoleChoices.WAITER,
            restaurant["id"],
        )
        chef = self.create_user(
            "swagger-chef@example.com",
            User.RoleChoices.CHEF,
            restaurant["id"],
        )

        menu_response = self.client.post(
            "/api/menu/",
            {
                "name": "Main Menu",
                "description": "Swagger workflow menu",
                "restuarant": restaurant["id"],
            },
            format="json",
        )
        self.assertEqual(menu_response.status_code, status.HTTP_201_CREATED, menu_response.data)
        menu = menu_response.data
        self.assertEqual(menu["restaurant_name"], restaurant["name"])

        burger_response = self.client.post(
            "/api/menuitems/",
            {
                "name": "API Burger",
                "category": "Main",
                "price": "12.50",
                "description": "Burger used in the Swagger workflow.",
                "menu": menu["id"],
            },
            format="json",
        )
        self.assertEqual(
            burger_response.status_code,
            status.HTTP_201_CREATED,
            burger_response.data,
        )
        burger = burger_response.data

        drink_response = self.client.post(
            "/api/menuitems/",
            {
                "name": "API Drink",
                "category": "Drinks",
                "price": "6.75",
                "description": "Drink used in the Swagger workflow.",
                "menu": menu["id"],
            },
            format="json",
        )
        self.assertEqual(
            drink_response.status_code,
            status.HTTP_201_CREATED,
            drink_response.data,
        )
        drink = drink_response.data

        table_response = self.client.post(
            "/api/tables/",
            {
                "restaurant": restaurant["id"],
                "table_number": 7,
                "capacity": 4,
                "status": "available",
            },
            format="json",
        )
        self.assertEqual(table_response.status_code, status.HTTP_201_CREATED, table_response.data)
        table = table_response.data
        self.assertEqual(table["restaurant_name"], restaurant["name"])
        self.assertEqual(table["status_display"], "Available")

        self.authenticate(waiter["email"])
        order_response = self.client.post(
            "/api/orders/",
            {
                "table": table["id"],
                "note": "Swagger workflow order",
                "items": [
                    {"menu_item": burger["id"], "quantity": 2},
                    {"menu_item": drink["id"], "quantity": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED, order_response.data)
        order = order_response.data
        self.assertEqual(order["status"], Order.StatusChoices.PENDING)
        self.assertEqual(order["status_display"], "Pending")
        self.assertEqual(order["restaurant_name"], restaurant["name"])
        self.assertEqual(order["table_number"], table["table_number"])
        self.assertEqual(order["waiter_email"], waiter["email"])
        self.assertEqual(Decimal(order["total_price"]), Decimal("31.75"))
        self.assertEqual(len(order["items"]), 2)
        self.assertEqual(Decimal(order["items"][0]["line_total"]), Decimal("25.00"))

        self.authenticate(chef["email"])
        chef_note_response = self.client.patch(
            f"/api/orders/{order['id']}/",
            {"note": "Chef must not edit notes"},
            format="json",
        )
        self.assertEqual(chef_note_response.status_code, status.HTTP_400_BAD_REQUEST)

        preparing_response = self.client.patch(
            f"/api/orders/{order['id']}/",
            {"status": Order.StatusChoices.PREPARING},
            format="json",
        )
        self.assertEqual(preparing_response.status_code, status.HTTP_200_OK, preparing_response.data)
        self.assertEqual(preparing_response.data["status"], Order.StatusChoices.PREPARING)

        ready_response = self.client.patch(
            f"/api/orders/{order['id']}/",
            {"status": Order.StatusChoices.READY},
            format="json",
        )
        self.assertEqual(ready_response.status_code, status.HTTP_200_OK, ready_response.data)
        self.assertEqual(ready_response.data["status"], Order.StatusChoices.READY)

        self.authenticate(waiter["email"])
        served_response = self.client.patch(
            f"/api/orders/{order['id']}/",
            {"status": Order.StatusChoices.SERVED},
            format="json",
        )
        self.assertEqual(served_response.status_code, status.HTTP_200_OK, served_response.data)
        self.assertEqual(served_response.data["status"], Order.StatusChoices.SERVED)

        terminal_edit_response = self.client.patch(
            f"/api/orders/{order['id']}/",
            {"note": "This edit must fail"},
            format="json",
        )
        self.assertEqual(terminal_edit_response.status_code, status.HTTP_400_BAD_REQUEST)

        list_response = self.client.get(
            "/api/orders/",
            {
                "status": Order.StatusChoices.SERVED,
                "search": "Swagger workflow",
                "ordering": "-created_at",
                "limit": 10,
            },
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK, list_response.data)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["id"], order["id"])

        schema_response = self.client.get("/api/schema/")
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        docs_response = self.client.get("/api/docs/")
        self.assertEqual(docs_response.status_code, status.HTTP_200_OK)
