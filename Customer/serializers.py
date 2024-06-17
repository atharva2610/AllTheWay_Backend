from rest_framework import serializers
from .models import Order, OrderItem, OrderPayment

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'status', 'payment_mode', 'item_amount',
            'total_amount', 'rated', 'customer', 'restaurant', 'delivery_location', 'restaurant_name', 'full_delivery_address', 'status_text', 'status_icon']


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['order', 'item', 'quantity', 'item_name', 'is_veg', 'price']
        extra_kwargs = {'order': {'read_only': True}}


    def create(self, validated_data):
        validated_data['order'] = self.context['order']
        return super().create(validated_data)
    

class OrderPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPayment
        fields = '__all__'