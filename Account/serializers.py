from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Account, DeliveryLocation
from Address.serializers import LocationSerializer

class AccountSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['id', 'email', 'name', 'phone', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        user = Account(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValidationError("The two passwords didn’t match.")
        return super().validate(attrs)
    


class UpdateAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['name', 'email', 'phone']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)



class DeliveryLocationSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)

    class Meta:
        model = DeliveryLocation
        fields = '__all__'

    def create(self, validated_data):
        validated_data['location'] = self.context['location']
        return super().create(validated_data)