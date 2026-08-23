from rest_framework import serializers
# pyrefly: ignore [missing-import]
from resturantorderingapi.validators import validate_no_html
from .models import MenuItem
from user.models import User


class MenuItemSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    restaurant_name = serializers.CharField(source="menu.restuarant.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "category",
            "price",
            "description",
            "menu",
            "menu_name",
            "restaurant_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "menu_name",
            "restaurant_name",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        return validate_no_html(value)

    def validate_category(self, value):
        return validate_no_html(value)

    def validate_description(self, value):
        return validate_no_html(value)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

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
