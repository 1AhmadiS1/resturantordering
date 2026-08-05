from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "role","restaurant"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def validate_role(self, value):
        request = self.context.get("request")

        if value == User.RoleChoices.PLATFORM_ADMIN:
            if not request or request.user.role != User.RoleChoices.PLATFORM_ADMIN:
                raise serializers.ValidationError("Only platform admins can assign this role.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def validate(self, value):
        role = value.get("role")
        restaurant = value.get("restaurant")

        if role in [User.RoleChoices.CHEF, User.RoleChoices.WAITER] and restaurant is None:
            raise serializers.ValidationError({
            "restaurant": "Restaurant is required for chef and waiter."
        })

        if role in [User.RoleChoices.OWNER, User.RoleChoices.PLATFORM_ADMIN] and restaurant is not None:
            raise serializers.ValidationError({
            "restaurant": "Owner and platform admin should not be assigned to a restaurant."
        })

        return value    

         