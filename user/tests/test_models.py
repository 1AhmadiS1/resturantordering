from django.test import TestCase
from user.models import User

class UserTest(TestCase):
    def setUp(self):
        self.password = "[PASSWORD]"

    def test_create_user(self):
        user = User.objects.create_user(
            email="user@gmail.com",
            password=self.password,
            first_name="Omar",
            last_name="Ahmad",
            role=User.RoleChoices.OWNER,
        )

        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.email, "user@gmail.com")
        self.assertEqual(user.first_name, "Omar")
        self.assertEqual(user.last_name, "Ahmad")
        self.assertEqual(user.role, User.RoleChoices.OWNER)
        self.assertEqual(str(user), "user@gmail.com")

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@gmail.com",
            password=self.password,
            first_name="Admin",
            last_name="User",
            role=User.RoleChoices.PLATFORM_ADMIN,
        )
        self.assertEqual(user.email, "admin@gmail.com")
        self.assertEqual(user.first_name, "Admin")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.role, User.RoleChoices.PLATFORM_ADMIN)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(str(user), "admin@gmail.com")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        
    def test_create_user_without_password(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="user@gmail.com",
                password=None,
                first_name="Omar",
                last_name="Ahmad",
                role=User.RoleChoices.OWNER,
            )
    