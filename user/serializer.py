from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "role"]
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
