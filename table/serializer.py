from user.models import User
from rest_framework import serializers
from .models import Table

class TableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Table
        fields = (
            "id",
            "restaurant",
            "restaurant_name",
            "table_number",
            "capacity",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "restaurant_name",
            "status_display",
            "created_at",
            "updated_at",
        )

    def validate_table_number(self, value):
        if value < 1:
            raise serializers.ValidationError("Table number must be at least 1.")
        return value

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        return value

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
