from django.db import models
# pyrefly: ignore [missing-import]
from restaurant.models import Restaurant


# Create your models here.
class Menu(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(null=True,blank=True)
    restuarant=models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu",
    )
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)    
    