from django.db import models

# Create your models here.
class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        SERVED = "served", "Served"
        CANCELLED = "cancelled", "Cancelled"
    restuarant=models.ForeignKey("restaurant.Restaurant",on_delete=models.CASCADE,related_name="orders")
    table=models.ForeignKey("table.Table",on_delete=models.CASCADE,related_name="orders")    
    total_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    status=models.CharField(max_length=10,choices=StatusChoices.choices,default=StatusChoices.PENDING)
    note = models.TextField(max_length=300,blank=True,null=True)
    waiter=models.ForeignKey("user.User",on_delete=models.SET_NULL,null=True,blank=True,related_name="orders")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table="order"

    def __str__(self):
        return f"Order {self.id}"
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="order_items")
    menu_item=models.ForeignKey("menuItem.MenuItem",on_delete=models.CASCADE,related_name="order_items")
    quantity=models.IntegerField(default=1)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table="order_item"

    def __str__(self):
        return f"Order {self.id} - {self.menu_item.name}"

    