from table.models import Table
from restaurant.models import Restaurant
from django.test import TestCase
from order.models import Order
from user.models import User

class OrderTest(TestCase):
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
            owner=self.user,
            address="123 main st",
            phone="1234567890",
            email="[EMAIL_ADDRESS]",
            description="Description",
        )
        self.table= Table.objects.create(
            restaurant=self.restaurant,
            number=1,
            capacity=4,
            is_available=True,
        )

