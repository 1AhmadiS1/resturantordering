from rest_framework import serializers
from .models import MenuItem
from user.models import User


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "category", "price", "description", "menu", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_menu(self, value):
        request = self.context.get("request")
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return value

        if user.role == User.RoleChoices.OWNER:
            if value.restuarant.owner != user:
                raise serializers.ValidationError("You can only add items to your own restaurant menu.")
            return value

        raise serializers.ValidationError("You are not allowed to add menu items.")