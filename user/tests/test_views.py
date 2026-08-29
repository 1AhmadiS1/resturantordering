from rest_framework import status
from rest_framework.test import APITestCase

from restaurant.models import Restaurant
from user.models import User


class CurrentUserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="waiter-profile@example.com",
            password="Profile-Test!2026",
            first_name="Profile",
            last_name="Waiter",
            role=User.RoleChoices.WAITER,
        )

    def test_authenticated_user_can_read_own_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["role"], User.RoleChoices.WAITER)
        self.assertNotIn("password", response.data)

    def test_unauthenticated_user_cannot_read_profile(self):
        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResetUserPasswordViewTests(APITestCase):
    password = "OriginalPassword!2026-Strong"
    new_password = "ResetPassword!2026-Strong"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin-reset@example.com",
            password=self.password,
            first_name="Platform",
            last_name="Admin",
        )
        self.owner = User.objects.create_user(
            email="owner-reset@example.com",
            password=self.password,
            first_name="Owner",
            last_name="One",
            role=User.RoleChoices.OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="other-owner-reset@example.com",
            password=self.password,
            first_name="Owner",
            last_name="Two",
            role=User.RoleChoices.OWNER,
        )
        self.restaurant = self.create_restaurant(
            "Owner Restaurant",
            "owner-restaurant-reset@example.com",
            self.owner,
        )
        self.other_restaurant = self.create_restaurant(
            "Other Restaurant",
            "other-restaurant-reset@example.com",
            self.other_owner,
        )
        self.waiter = User.objects.create_user(
            email="waiter-reset@example.com",
            password=self.password,
            first_name="Waiter",
            last_name="One",
            role=User.RoleChoices.WAITER,
            restaurant=self.restaurant,
        )
        self.other_waiter = User.objects.create_user(
            email="other-waiter-reset@example.com",
            password=self.password,
            first_name="Waiter",
            last_name="Two",
            role=User.RoleChoices.WAITER,
            restaurant=self.other_restaurant,
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

    def reset_url(self, user):
        return f"/api/users/{user.id}/reset-password/"

    def valid_payload(self):
        return {
            "new_password": self.new_password,
            "confirm_password": self.new_password,
        }

    def test_platform_admin_can_reset_any_user_password(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.reset_url(self.owner), self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password(self.new_password))

    def test_owner_can_reset_own_restaurant_staff_password(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(self.reset_url(self.waiter), self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.waiter.refresh_from_db()
        self.assertTrue(self.waiter.check_password(self.new_password))

    def test_owner_cannot_reset_another_restaurant_staff_password(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(self.reset_url(self.other_waiter), self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_waiter.refresh_from_db()
        self.assertTrue(self.other_waiter.check_password(self.password))

    def test_waiter_cannot_reset_passwords(self):
        self.client.force_authenticate(self.waiter)

        response = self.client.post(self.reset_url(self.other_waiter), self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
