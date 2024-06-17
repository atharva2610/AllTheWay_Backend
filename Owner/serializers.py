from rest_framework.serializers import ModelSerializer, ReadOnlyField, ValidationError
from .models import Restaurant, Rating, Cuisine, MenuItem
from Address.serializers import LocationSerializer


class RatingSerializer(ModelSerializer):
    average_rating = ReadOnlyField()
    
    class Meta:
        model = Rating
        fields = '__all__'


class RestaurantSerializer(ModelSerializer):
    rating = RatingSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'owner', 'license', 'phone', 'image', 'location', 'veg', 'temporary_close', 'rating']


    def create(self, validated_data):
        validated_data['location'] = self.context['location']
        return super().create(validated_data)
    

class CuisineSerializer(ModelSerializer):
    
    class Meta:
        model = Cuisine
        fields = '__all__'


class MenuItemSerializer(ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields = '__all__'