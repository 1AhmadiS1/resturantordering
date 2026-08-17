from rest_framework import serializers
from .models import Menu
from user.models import User


class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restuarant.name", read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "name",
            "description",
            "restuarant",
            "restaurant_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "restaurant_name", "created_at", "updated_at"]

    def validate_restuarant(self, value):
        request = self.context.get("request")
        user = request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return value

        if user.role == User.RoleChoices.OWNER:
            if value.owner != user:
                raise serializers.ValidationError("You can only create menus for your own restaurant.")
            return value

        raise serializers.ValidationError("You are not allowed to create menus.")
