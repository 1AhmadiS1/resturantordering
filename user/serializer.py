from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "restaurant",
            "restaurant_name",
        ]
        read_only_fields = ["id", "restaurant_name"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def validate_role(self, value):
        request = self.context.get("request")

        if value == User.RoleChoices.PLATFORM_ADMIN:
            if not request or request.user.role != User.RoleChoices.PLATFORM_ADMIN:
                raise serializers.ValidationError("Only platform admins can assign this role.")

        return value

    def validate_password(self, value):
        if self.instance is not None:
            raise serializers.ValidationError(
                "Use the change-password endpoint to update a password."
            )

        try:
            password_validation.validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(list(error.messages)) from error
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            raise serializers.ValidationError({"password": "Password cant be updated here"})
        for attr,value in validated_data.items():
            setattr(instance,attr,value)    
        instance.save()
        return instance

    def validate(self, attrs):
        request = self.context.get("request")
        actor = request.user if request else None
        role = attrs.get("role", getattr(self.instance, "role", None))
        restaurant = attrs.get(
            "restaurant",
            getattr(self.instance, "restaurant", None),
        )

        if role in [User.RoleChoices.CHEF, User.RoleChoices.WAITER] and restaurant is None:
            raise serializers.ValidationError({
                "restaurant": "Restaurant is required for chef and waiter."
            })

        if role in [User.RoleChoices.OWNER, User.RoleChoices.PLATFORM_ADMIN] and restaurant is not None:
            raise serializers.ValidationError({
                "restaurant": "Owner and platform admin should not be assigned to a restaurant."
            })

        if actor and actor.role == User.RoleChoices.OWNER:
            if role not in [User.RoleChoices.CHEF, User.RoleChoices.WAITER]:
                raise serializers.ValidationError({
                    "role": "Owners may only create or manage waiter and chef accounts."
                })
            if restaurant is None or restaurant.owner_id != actor.id:
                raise serializers.ValidationError({
                    "restaurant": "You may only assign staff to your own restaurant."
                })

        return attrs


class UserCreateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True,
                "help_text": "Required when creating a user; use change-password later.",
            }
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self,value):
        request=self.context.get("request")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("You are not authorized to change password")
        user=request.user
        if not user.check_password(value["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        if value["old_password"] == value["new_password"]:
            raise serializers.ValidationError({
                "new_password": "New password must be different from the old password."
            })

        try:
            password_validation.validate_password(value["new_password"], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({
                "new_password": list(error.messages)
            }) from error
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class ChangePasswordResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
