from rest_framework import serializers
from .models import Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "name", "description", "restuarant", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

        


