from rest_framework import serializers
from resturantorderingapi.validators import validate_no_html
from .models import Restaurant
from user.models import User

class ResturantSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model=Restaurant
        fields=['id','name','owner','owner_email','address','phone','email','description','created_at','updated_at']
        read_only_fields=['id','owner_email','created_at','updated_at']

    def validate_name(self, value):
        return validate_no_html(value)

    def validate_address(self, value):
        return validate_no_html(value)

    def validate_phone(self, value):
        return validate_no_html(value)

    def validate_description(self, value):
        return validate_no_html(value)
    
    def validate_owner(self,value):
        if value.role != User.RoleChoices.OWNER:
            raise serializers.ValidationError("The selected user must have the owner role.")

        request = self.context.get("request")
        if (
            self.instance
            and request
            and request.user.role == User.RoleChoices.OWNER
            and value.id != request.user.id
        ):
            raise serializers.ValidationError(
                "Only a platform admin can transfer a restaurant to another owner."
            )
        return value
