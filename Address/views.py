from .serializers import StateSerializer, CitySerializer, LocationSerializer
from rest_framework.generics import ListAPIView
from .models import State, City, Location
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ListStates(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer


class ListCities(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class UpdateLocation(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            location = Location.objects.get(id=pk, is_deleted=False)
            serializer = LocationSerializer(instance=location, data=request.data)
            if serializer.is_valid():
                if request.data['city'] == '':
                    return Response({'city': ['City is required']}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Location.DoesNotExist:
            return Response('Location Not Found!', status=status.HTTP_404_NOT_FOUND)
