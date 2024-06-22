from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from Customer.serializers import OrderSerializer
from .serializers import RestaurantSerializer, CuisineSerializer, MenuItemSerializer
from Address.serializers import LocationSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Restaurant, Cuisine, MenuItem
from rest_framework.permissions import IsAuthenticated
from Customer.models import Order, OrderItem
from Customer.serializers import OrderSerializer, OrderItemSerializer
from channels.layers import get_channel_layer
from django.db import models


invalid_restaurant_response = Response("Restaurant Not Found!", status=status.HTTP_404_NOT_FOUND)
no_permission_response = Response("You can not perform this action!", status=status.HTTP_403_FORBIDDEN)

def get_restaurant(restaurant_id):
    exist = False
    restaurant = None
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id, is_deleted=False)
        exist = True
    except Restaurant.DoesNotExist:
        pass
    return [exist, restaurant]


def is_restaurant_owner(restaurant, user_id):
    return restaurant.owner.id == user_id


class AllRestaurantsByOwner(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        restaurants = Restaurant.objects.filter(owner__id=request.user.id, is_deleted=False)
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUpdateDeleteRestaurant(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if Restaurant.objects.filter(owner__id=request.user.id).count() >= 5:
            return Response('You have reached maximum Restaurant limit!', status=status.HTTP_403_FORBIDDEN)
        
        request.data['owner'] = request.user.id
        restaurant_serializer = RestaurantSerializer(data=request.data)
        if not restaurant_serializer.is_valid():
            return Response(restaurant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        location_serializer = LocationSerializer(data=request.data)
        if not location_serializer.is_valid():
            return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        location = location_serializer.save()
        restaurant_serializer.context['location'] = location
        restaurant_serializer.save()

        return Response(restaurant_serializer.data, status=status.HTTP_201_CREATED)
    

    def patch(self, request, pk, format=None):
        [exist, restaurant] = get_restaurant(pk)
        if exist:
            if is_restaurant_owner(restaurant, request.user.id):
                serializer = RestaurantSerializer(data=request.data, instance=restaurant, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return no_permission_response
        else:
            return invalid_restaurant_response
        

    def delete(self, request, pk, format=None):
        [exist, restaurant] = get_restaurant(pk)
        if exist:
            if is_restaurant_owner(restaurant, request.user.id):
                orders = restaurant.orders.filter(status__in=['ordered', 'preparing', 'prepared', 'delivering'])
                if len(orders):
                    return Response('Complete the existing Orders to delete!', status=status.HTTP_400_BAD_REQUEST)
                else:
                    restaurant.is_deleted = True
                    restaurant.save()
                    return Response('Restaurant Deleted Successfully!', status=status.HTTP_204_NO_CONTENT)
            else:
                return no_permission_response
        else:
            return invalid_restaurant_response


class ChangeRestaurantBanner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        [exist, restaurant] = get_restaurant(pk)
        if exist:
            if is_restaurant_owner(restaurant, request.user.id):
                serializer = RestaurantSerializer(data=request.data, instance=restaurant, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return no_permission_response
        else:
            return invalid_restaurant_response
    

class RetrieveRestaurant(APIView):
    
    def get(self, request, pk, format=None):
        [exist, restaurant] = get_restaurant(pk)
        if exist:
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return invalid_restaurant_response


class CuisinesByRestaurant(APIView):

    def get(self, request, restaurant_id, format=None):
        [exist, restaurant] = get_restaurant(restaurant_id)
        if exist:
            distinct_cuisines_id = MenuItem.objects.filter(restaurant__id=restaurant.id, is_deleted=False).values('cuisine').distinct()
            cuisines = Cuisine.objects.filter(id__in=distinct_cuisines_id)
            serializer = CuisineSerializer(cuisines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return invalid_restaurant_response


class ListCuisines(APIView):

    def get(self, request, format=None):
        cuisines = Cuisine.objects.all()
        serializer = CuisineSerializer(cuisines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListMenuItems(APIView):

    def get(self, request, restaurant_id, format=None):
        [exist, restaurant] = get_restaurant(restaurant_id)
        if exist:
            items = MenuItem.objects.filter(restaurant__id=restaurant.id, is_deleted=False)
            serializer = MenuItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return invalid_restaurant_response
        

class RetrieveMenuItem(APIView):

    def get(self, request, pk, format=None):
        try:
            menuitem = MenuItem.objects.get(id=pk, is_deleted=False)
            serializer = MenuItemSerializer(menuitem)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response("Item Not Found!", status=status.HTTP_404_NOT_FOUND)
        

class CreateUpdateDeleteMenuItem(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        restaurant = Restaurant.objects.get(id=request.data.get('restaurant'))
        if restaurant.owner.id != request.user.id:
                return Response('You are not the Owner of this restaurant.', status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def patch(self, request, pk, format=None):
        try:
            item = MenuItem.objects.get(id=pk, is_deleted=False)
            if is_restaurant_owner(item.restaurant, request.user.id):
                serializer = MenuItemSerializer(data=request.data, instance=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return no_permission_response
        except MenuItem.DoesNotExist:
            return Response('Item Not Found!', status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk, format=None):
        try:
            item = MenuItem.objects.get(id=pk, is_deleted=False)
            orders = Order.objects.filter(status__in=['ordered', 'preparing', 'prepared', 'delivering'], restaurant__id=item.restaurant.id)
            order_items = OrderItem.objects.filter(order__in=orders, item__id=item.id)
            if len(order_items):
                return Response('Active Orders include this item!', status=status.HTTP_400_BAD_REQUEST)
            else:
                item.is_deleted = True
                item.save()
                return Response('Item Deleted Successfully!', status=status.HTTP_204_NO_CONTENT)
        except MenuItem.DoesNotExist:
            return Response('Item Not Found!', status=status.HTTP_404_NOT_FOUND)


class ChangeItemImage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            item = MenuItem.objects.get(id=pk, is_deleted=False)
            if is_restaurant_owner(item.restaurant, request.user.id):
                serializer = MenuItemSerializer(data=request.data, instance=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return no_permission_response
        except MenuItem.DoesNotExist:
            return Response('Item Not Found', status=status.HTTP_404_NOT_FOUND)


class RestaurantOrdersList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, restaurant_id, tag, format=None):
        [exist, restaurant] = get_restaurant(restaurant_id)

        if exist:
            if tag not in ['active', 'new', 'past']:
                return Response('Invalid Order Status!', status=status.HTTP_400_BAD_REQUEST)
            if tag == 'active':
                orders = restaurant.orders.filter(status__in=['preparing', 'prepared', 'delivering'])
            elif tag == 'new':
                orders = restaurant.orders.filter(status='ordered')
            else:
                orders = restaurant.orders.filter(status__in=['delivered', 'by_customer', 'restaurant_rejected', 'out_of_stock', 'accident'])
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return invalid_restaurant_response
        

class RetrieveUpdateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            order = Order.objects.get(id=pk)
            if order.restaurant.owner.id == request.user.id:
                items = OrderItem.objects.filter(order__id=order.id)
                order_serializer = OrderSerializer(order)
                items_serializer = OrderItemSerializer(items, many=True)
                return Response({'order': order_serializer.data, 'items': items_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response('You cannot access this Order!', status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response('Order Not Found!', status=status.HTTP_404_NOT_FOUND)
        
    
    def patch(self, request, pk, format=None):
        try:
            order = Order.objects.get(id=pk)
            if order.restaurant.owner.id == request.user.id:
                serializer = OrderSerializer(data=request.data, instance=order, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    channel_layer = get_channel_layer()
                    data = serializer.data
                    data['customer'] = str(data['customer'])
                    data['restaurant'] = str(data['restaurant'])
                    async_to_sync(channel_layer.group_send)(data['customer'], {'type': 'notify', 'message': data})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('You cannot access this Order!', status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response('Order Not Found!', status=status.HTTP_404_NOT_FOUND)
        

class OrderSummary(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        [exist, restaurant] = get_restaurant(pk)
        if exist:
            orders = Order.objects.filter(restaurant__id=restaurant.id)
            if orders.first().restaurant.id == restaurant.id:
                data = {
                    'info': {
                            'total_orders': 0,
                            'delivered_orders': 0,
                            'active_orders': 0,
                            'cancelled_orders': 0,
                            'total_revenue': 0
                        },
                    'items': []
                }

                for order in orders:
                    data['info']['total_orders'] += 1
                    if order.status == 'delivered':
                        data['info']['delivered_orders'] += 1
                        data['info']['total_revenue'] += order.item_amount
                    elif order.status in ['ordered', 'preparing', 'prepared', 'delivering']:
                        data['info']['active_orders'] += 1
                    else:
                        data['info']['cancelled_orders'] += 1

                menu_items_with_frequency = MenuItem.objects.filter(orderitem__order__restaurant__id=restaurant.id, is_deleted=False).annotate(order_frequency=models.Count('orderitem')).order_by('-order_frequency')
                for item in menu_items_with_frequency:
                    data['items'].append({'id': item.id, 'name': item.name, 'order_frequency': item.order_frequency})
                
                return Response(data, status=status.HTTP_200_OK)
            else:
                return no_permission_response
        else:
            return invalid_restaurant_response
            