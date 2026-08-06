from django.db import models

# Create your models here.

class Table(models.Model):
    class StatusChoices(models.TextChoices):
        AVAILABLE="available","Available"
        OCCUPIED="occupied","Occupied"
        RESERVED="reserved","Reserved"
        INACTIVE="inactive","Inactive"

    restaurant=models.ForeignKey("restaurant.Restaurant",on_delete=models.CASCADE,related_name="tables")
    table_number=models.PositiveSmallIntegerField()
    capacity = models.PositiveIntegerField(default=4)    
    status=models.CharField(max_length=15,choices=StatusChoices.choices,default=StatusChoices.AVAILABLE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=("restaurant","table_number")


    def __str__(self):
        return f"Table {self.table_number}"
        