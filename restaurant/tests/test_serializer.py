from django.test import TestCase

from restaurant.serializer import ResturantSerializer
from user.models import User


class RestaurantSerializerTest(TestCase):
    password = "FocusedTests!2026-Strong"

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password=self.password,
            first_name="First",
            last_name="Owner",
            role=User.RoleChoices.OWNER,
        )

    def test_restaurant_name_rejects_html(self):
        serializer = ResturantSerializer(
            data={
                "name": "<script>alert('xss')</script>",
                "owner": self.owner.id,
                "address": "Test Address",
                "phone": "123456789",
                "email": "restaurant@example.com",
                "description": "Test restaurant",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
