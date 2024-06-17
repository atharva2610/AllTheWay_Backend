from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from Owner.models import Restaurant, Rating, MenuItem, Cuisine
from Address.models import City
from Owner.serializers import RestaurantSerializer, CuisineSerializer, MenuItemSerializer
from .models import Order, OrderItem, OrderPayment
from .serializers import OrderPaymentSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import razorpay
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def get_cuisines_by_restaurant(restaurants):
    restaurant_with_menu_items = []
    cuisines_by_restaurants = []
    for restaurant in restaurants:
        menu = restaurant.menuitem.all()
        if(menu):
            distinct_cuisines_id = menu.values('cuisine').distinct()
            cuisines = Cuisine.objects.filter(id__in=distinct_cuisines_id)
            serializer = CuisineSerializer(cuisines, many=True)
            cuisines_by_restaurants.append(serializer.data)
            restaurant_with_menu_items.append(restaurant)

    return [restaurant_with_menu_items, cuisines_by_restaurants]

def home(request):
    return render(request, 'home.html')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject'
    success_message = "We've emailed you Password Reset link, if an account exists with the email."
    success_url = reverse_lazy('home')


class StartPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        amount = request.data.get('amount')
        client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))
        payment = client.order.create({'amount': amount*100, 'currency': 'INR', 'payment_capture': '0'})
        serializer = OrderPaymentSerializer(data={'amount': amount, 'payment_id': payment['id']})
        if serializer.is_valid():
            serializer.save()
            return Response({"payment": payment,"order": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class PaymentSuccess(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            order_payment = OrderPayment.objects.get(payment_id=request.data.get('razorpay_order_id'))
            client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))
            check = client.utility.verify_payment_signature(request.data)
            print(check)
            if check:
                order_payment.isPaid = True
                order_payment.save()
                serializer = OrderPaymentSerializer(order_payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response('Something went wrong', status=status.HTTP_400_BAD_REQUEST)
        except OrderPayment.DoesNotExist:
            return Response('Data Not Found!', status=status.HTTP_404_NOT_FOUND)


class ListRestaurantByCity(APIView):

    def get(self, request, city_id, format=None):
        try:
            restaurants = Restaurant.objects.filter(location__city__id=city_id, is_deleted=False)
            restaurants, cuisines_by_restaurants = get_cuisines_by_restaurant(restaurants)

            restaurants_serializer = RestaurantSerializer(restaurants, many=True)
            return Response({'restaurants': restaurants_serializer.data, 'cuisines_by_restaurants': cuisines_by_restaurants}, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response('City Not Found!', status=status.HTTP_404_NOT_FOUND)


class ListFavoriteRestaurants(APIView):

    def get(self, request, favorites, format=None):
        try:
            favorites = favorites.split(",")
            restaurants = Restaurant.objects.filter(id__in=favorites, is_deleted=False)
            restaurants, cuisines_by_restaurants = get_cuisines_by_restaurant(restaurants)

            restaurants_serializer = RestaurantSerializer(restaurants, many=True)
            return Response({'restaurants': restaurants_serializer.data, 'cuisines_by_restaurants': cuisines_by_restaurants}, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response('Restaurant Not Found!', status=status.HTTP_404_NOT_FOUND)


class ListSearchedRestaurants(APIView):
    def get(self, request, city_id, search_for, format=None):
        try:
            restaurants = Restaurant.objects.filter(location__city__id=city_id, name__icontains=search_for, is_deleted=False)
            restaurants, cuisines_by_restaurants = get_cuisines_by_restaurant(restaurants)

            restaurants_serializer = RestaurantSerializer(restaurants, many=True)
            return Response({'restaurants': restaurants_serializer.data, 'cuisines_by_restaurants': cuisines_by_restaurants}, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response('Invalid City Name!', status=status.HTTP_404_NOT_FOUND)
        

class ListSearchedDishes(APIView):
    def get(self, request, city_id, search_for, format=None):
        try:
            restaurants = Restaurant.objects.filter(location__city__id=city_id, is_deleted=False)
            dishes_by_restaurant = []
            for restaurant in restaurants:
                items = restaurant.menuitem.filter(name__icontains=search_for, is_deleted=False)
                if (items):
                    serializer = RestaurantSerializer(restaurant)
                    dishes_by_restaurant.append({
                        'restaurant': serializer.data,
                        'items': MenuItemSerializer(items, many=True).data,
                    })
            return Response(dishes_by_restaurant, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response('Invalid City Name!', status=status.HTTP_404_NOT_FOUND)


class CartItems(APIView):

    def get(self, request, items, format=None):
        items = MenuItem.objects.filter(id__in=items.split(","), is_deleted=False)
        if len(items):
            serialize = MenuItemSerializer(items, many=True)
            print(items)
            return Response(serialize.data, status=status.HTTP_200_OK)
        else:
            return Response('Cart Item Not Found', status=status.HTTP_404_NOT_FOUND)
        

class ListOrders(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer__id=request.user.id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ListOrderItems(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id, format=None):
        items = OrderItem.objects.filter(order__id=order_id)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveCreateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            order = Order.objects.get(id=pk)
            if order.customer.id == request.user.id:
                items = OrderItem.objects.filter(order__id=order.id)
                order_serializer = OrderSerializer(order)
                items_serializer = OrderItemSerializer(items, many=True)
                return Response({'order': order_serializer.data, 'items': items_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response('You are not the Owner of this Restaurant', status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response('Order Not Found!', status=status.HTTP_404_NOT_FOUND)

    
    def post(self, request, format=None):
        try:
            select_items = MenuItem.objects.filter(id__in=request.data['cart'].keys())
            items = []
            for [item_id, quantity] in request.data['cart'].items():
                items.append({'item': item_id, 'quantity': quantity, 'price': select_items.get(id=item_id).price})

            request.data['customer'] = str(request.user.id)
            order_serializer = OrderSerializer(data=request.data)

            if order_serializer.is_valid():
                order_items_serializer = OrderItemSerializer(data=items, many=True)

                if order_items_serializer.is_valid():
                    order = order_serializer.save()
                    order_items_serializer.context['order'] = order
                    order_items_serializer.save()
                    if request.data.get('payment_mode') == 'online':
                        try:
                            order_payment = OrderPayment.objects.get(id=request.data['payment_id'])
                            order_payment.order = order
                            order_payment.save()
                        except OrderPayment.DoesNotExist:
                            return Response('Payment Not Found!', status=status.HTTP_404_NOT_FOUND)
                    channel_layer = get_channel_layer()
                    data = order_serializer.data
                    data['customer'] = str(data['customer'])
                    data['restaurant'] = str(data['restaurant'])
                    async_to_sync(channel_layer.group_send)(data['restaurant'], {'type': 'notify', 'message': data})
                    return Response('Order Placed Successfully!', status=status.HTTP_201_CREATED)
                else:
                    return Response(order_items_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except MenuItem.DoesNotExist:
            return Response('Item Not Found', status=status.HTTP_404_NOT_FOUND)
        

    def patch(self, request, pk, format=None):
        try:
            order = Order.objects.get(id=pk)
            if order.customer.id == request.user.id:
                if 'status' in request.data.keys() and len(request.data.keys()):
                    serializer = OrderSerializer(data=request.data, instance=order, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        channel_layer = get_channel_layer()
                        data = serializer.data
                        data['customer'] = str(data['customer'])
                        data['restaurant'] = str(data['restaurant'])
                        async_to_sync(channel_layer.group_send)(data['restaurant'], {'type': 'notify', 'message': data})
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response('Cannot Update Order!', status=status.HTTP_403_FORBIDDEN)
            else:
                return Response('This Is Not Your Order', status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response('Order Not Found!', status=status.HTTP_404_NOT_FOUND)


class RateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id, format=None):
        try:
            order = Order.objects.get(id=order_id)
            if order.customer.id == request.user.id:
                if order.rated:
                    return Response('You have already rated the Order!', status=status.HTTP_400_BAD_REQUEST)
                else:
                    restaurant_rating = Rating.objects.get(restaurant__id=order.restaurant.id)
                    order_rating = request.data.get('rating')
                    if order_rating >= 1 and order_rating <= 5:
                        restaurant_rating.total_rating += order_rating
                        restaurant_rating.no_of_ratings += 1
                        restaurant_rating.save()
                        order.rated = True
                        order.save()
                        serializer = OrderSerializer(order)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response('Invalid Rating!', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('You cannot access this Order!', status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response('Order Not Found!', status=status.HTTP_404_NOT_FOUND)