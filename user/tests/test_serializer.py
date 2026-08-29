from types import SimpleNamespace

from django.test import TestCase

from restaurant.models import Restaurant
from user.models import User
from user.serializer import (
    ChangePasswordSerializer,
    ResetUserPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class UserSerializerTest(TestCase):
    password = "FocusedTests!2026-Strong"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
            first_name="Platform",
            last_name="Admin",
        )
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password=self.password,
            first_name="First",
            last_name="Owner",
            role=User.RoleChoices.OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="other-owner@example.com",
            password=self.password,
            first_name="Other",
            last_name="Owner",
            role=User.RoleChoices.OWNER,
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
        self.waiter = User.objects.create_user(
            email="waiter@example.com",
            password=self.password,
            first_name="Existing",
            last_name="Waiter",
            role=User.RoleChoices.WAITER,
            restaurant=self.restaurant,
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

    def request_for(self, user):
        return SimpleNamespace(user=user)

    def test_admin_can_create_owner_and_password_is_hashed(self):
        serializer = UserCreateSerializer(
            data={
                "email": "new-owner@example.com",
                "password": self.password,
                "first_name": "New",
                "last_name": "Owner",
                "role": User.RoleChoices.OWNER,
            },
            context={"request": self.request_for(self.admin)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertNotIn("password", serializer.data)

    def test_owner_can_create_waiter_for_own_restaurant(self):
        serializer = UserCreateSerializer(
            data={
                "email": "new-waiter@example.com",
                "password": self.password,
                "first_name": "New",
                "last_name": "Waiter",
                "role": User.RoleChoices.WAITER,
                "restaurant": self.restaurant.id,
            },
            context={"request": self.request_for(self.owner)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.restaurant, self.restaurant)

    def test_user_name_rejects_html(self):
        serializer = UserCreateSerializer(
            data={
                "email": "xss-user@example.com",
                "password": self.password,
                "first_name": "<script>alert('xss')</script>",
                "last_name": "User",
                "role": User.RoleChoices.OWNER,
            },
            context={"request": self.request_for(self.admin)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_owner_cannot_assign_staff_to_another_restaurant(self):
        serializer = UserCreateSerializer(
            data={
                "email": "foreign-waiter@example.com",
                "password": self.password,
                "first_name": "Foreign",
                "last_name": "Waiter",
                "role": User.RoleChoices.WAITER,
                "restaurant": self.other_restaurant.id,
            },
            context={"request": self.request_for(self.owner)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("restaurant", serializer.errors)

    def test_owner_cannot_create_another_owner(self):
        serializer = UserCreateSerializer(
            data={
                "email": "forbidden-owner@example.com",
                "password": self.password,
                "first_name": "Forbidden",
                "last_name": "Owner",
                "role": User.RoleChoices.OWNER,
            },
            context={"request": self.request_for(self.owner)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

    def test_partial_update_uses_existing_role_and_restaurant(self):
        serializer = UserSerializer(
            instance=self.waiter,
            data={"first_name": "Updated"},
            partial=True,
            context={"request": self.request_for(self.owner)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.restaurant, self.restaurant)
        self.assertEqual(user.role, User.RoleChoices.WAITER)

    def test_password_cannot_be_changed_through_user_update(self):
        serializer = UserSerializer(
            instance=self.waiter,
            data={"password": "AnotherStrong!2026-Password"},
            partial=True,
            context={"request": self.request_for(self.owner)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_change_password_rejects_wrong_old_password(self):
        serializer = ChangePasswordSerializer(
            instance=self.waiter,
            data={
                "old_password": "WrongPassword!2026",
                "new_password": "AnotherStrong!2026-Password",
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_change_password_hashes_valid_new_password(self):
        new_password = "AnotherStrong!2026-Password"
        serializer = ChangePasswordSerializer(
            instance=self.waiter,
            data={
                "old_password": self.password,
                "new_password": new_password,
            },
            context={"request": self.request_for(self.waiter)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.waiter.refresh_from_db()
        self.assertTrue(self.waiter.check_password(new_password))

    def test_reset_user_password_hashes_valid_new_password(self):
        new_password = "ResetPassword!2026-Strong"
        serializer = ResetUserPasswordSerializer(
            instance=self.waiter,
            data={
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.waiter.refresh_from_db()
        self.assertTrue(self.waiter.check_password(new_password))

    def test_reset_user_password_requires_matching_confirmation(self):
        serializer = ResetUserPasswordSerializer(
            instance=self.waiter,
            data={
                "new_password": "ResetPassword!2026-Strong",
                "confirm_password": "DifferentPassword!2026-Strong",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)
