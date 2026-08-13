from django.test import TestCase
from restaurant.models import Restaurant
from user.models import User

class RestaurantTest(TestCase):
    def setUp(self):
        self.owner= User.objects.create_user(
            email="user@gmail.com",
            password="[PASSWORD]",
            first_name="Omar",
            last_name="Ahmad",
            role=User.RoleChoices.OWNER,
        )
        self.restaurant= Restaurant.objects.create(
            name="Restaurant",
            owner=self.owner,
            address="123 main st",
            phone="1234567890",
            email="[EMAIL_ADDRESS]",
            description="Description",
        )

        
    def test_restaurant(self):
        # Test that the restaurant is created correctly
        restaurant=self.restaurant
        self.assertEqual(restaurant.name, "Restaurant")
        self.assertEqual(restaurant.owner, self.owner)
        self.assertEqual(restaurant.address, "123 main st")
        self.assertEqual(restaurant.phone, "1234567890")
        self.assertEqual(restaurant.email, "[EMAIL_ADDRESS]")
        self.assertEqual(restaurant.description, "Description")
        self.assertEqual(str(restaurant), "Restaurant")

        
