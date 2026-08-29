from rest_framework import status
from rest_framework.test import APITestCase

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
