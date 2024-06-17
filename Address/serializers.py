from rest_framework.serializers import ModelSerializer, ReadOnlyField, ValidationError
from .models import State, City, Location

class StateSerializer(ModelSerializer):

    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(ModelSerializer):
    state = StateSerializer()

    class Meta:
        model = City
        fields = '__all__'


class LocationSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)
    full_address = ReadOnlyField()
    
    class Meta:
        model = Location
        fields = ['id', 'house_no', 'area', 'pincode', 'city', 'full_address']

    def create(self, validated_data):
        validated_data['city'] = City.objects.get(id=self.initial_data['city'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['city'] = City.objects.get(id=self.initial_data['city'])
        return super().update(instance, validated_data)