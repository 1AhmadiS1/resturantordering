from django.db import models
from user.models import User
# Create your models here.
class Restaurant(models.Model):
    name=models.CharField(max_length=100)
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='restaurants')
    address=models.CharField(max_length=100)
    phone=models.CharField(max_length=20)
    email=models.EmailField(unique=True)
    description=models.TextField()

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name