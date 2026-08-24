from django.db import models

# Create your models here.

class MenuItem(models.Model):
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    menu=models.ForeignKey('menu.Menu',on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to="menu-items/",null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
