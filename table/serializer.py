from user.models import User
from rest_framework import serializers
from .models import Table

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            "id",
            "restaurant",
            "table_number",
            "capacity",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_restaurant(self,value):
        request=self.context.get("request")
        user=request.user
        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return value
        if user.role == User.RoleChoices.OWNER:
            if value.owner !=user:
                raise serializers.ValidationError("You can only create tables for your own restaurant.")
            return value
        raise serializers.ValidationError("You are not allowed to create tables.")
        
    