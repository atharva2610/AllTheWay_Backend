from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from Address.serializers import LocationSerializer
from Owner.models import Restaurant

from random import randint
from .models import DeliveryLocation
from .serializers import AccountSerializer, DeliveryLocationSerializer, UpdateAccountSerializer, ChangePasswordSerializer
from .custom_permissions import UnauthenticatedOnly


class UserRegistrationApiView(APIView):
    permission_classes = [UnauthenticatedOnly]

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Account Created Successfully!", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = AccountSerializer(request.user)
        token = RefreshToken.for_user(request.user)
        return Response({'user':serializer.data, 'newToken':str(token.access_token)}, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UpdateAccountSerializer(data=request.data, instance=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        account = request.user
        account.email = str(randint(0,99))+'deleted_'+str(randint(0,99))+account.email
        account.is_active = False
        account.save()
        return Response('Account Deleted Successfully!', status=status.HTTP_204_NO_CONTENT)


class ChangePasswordApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'old_password': ['Incorrect old password.']}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchedDeliveryLocationsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, restaurant_id):
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id, is_deleted=False)
            delivery_locations = DeliveryLocation.objects.filter(user__id=self.request.user.id, is_deleted=False, location__city__id=restaurant.location.city.id)
            serializer = DeliveryLocationSerializer(delivery_locations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response("Restaurant Not Found!", status=status.HTTP_404_NOT_FOUND)
        

class ListCreateDeleteDeliveryLocationApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        delivery_locations = DeliveryLocation.objects.filter(user__id=request.user.id, is_deleted=False)
        serializer = DeliveryLocationSerializer(delivery_locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request, format=None):
        if DeliveryLocation.objects.filter(user__id=request.user.id).count() == 4:
            return Response('You can not add more Addresses!', status=status.HTTP_403_FORBIDDEN)
        location_serializer = LocationSerializer(data=request.data)
        if location_serializer.is_valid():
            delivery_location_serializer = DeliveryLocationSerializer(data={'user':request.user.id})
            if delivery_location_serializer.is_valid():
                location = location_serializer.save()
                delivery_location_serializer.context['location'] = location
                delivery_location_serializer.save()
                return Response(delivery_location_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(delivery_location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, pk, format=None):
        try:
            delivery_location = DeliveryLocation.objects.get(id=pk)
            delivery_location.is_deleted = True
            delivery_location.save()
            return Response('Delivery Location Deleted Successfully!', status=status.HTTP_204_NO_CONTENT)
        except DeliveryLocation.DoesNotExist:
            return Response('Delivery Location Not Found!', status=status.HTTP_404_NOT_FOUND)
    

class LoginApiView(APIView):
    permission_classes = [UnauthenticatedOnly]

    def post(self, request):
        try:
            user_obj = authenticate(email=request.data.get('email'), password=request.data.get('password'))
            if user_obj is not None:
                token = RefreshToken.for_user(user_obj)
                serializer = AccountSerializer(user_obj)
                return Response({'user':serializer.data, 'authToken':str(token.access_token)}, status=status.HTTP_200_OK)
            else:
                return Response({'non_field_errors': ['invalid username or password']}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'non_field_errors': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)