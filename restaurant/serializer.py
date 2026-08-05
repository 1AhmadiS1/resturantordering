from rest_framework import serializers
from .models import Restaurant
from user.models import User

class ResturantSerializer(serializers.ModelSerializer):
    class Meta:
        model=Restaurant
        fields=['id','name','owner','address','phone','email','description','created_at','updated_at']
        read_only_fields=['id','created_at','updated_at']
    
    def validate_owner(self,value):
        if value.role != User.RoleChoices.OWNER:
            raise serializers.ValidationError("Owner must be an owner")
        return value    

        