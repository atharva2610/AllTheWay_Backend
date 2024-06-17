from django.urls import path
from .views import ListStates, ListCities, UpdateLocation

urlpatterns = [
    path('states/', ListStates.as_view()),
    path('cities/', ListCities.as_view()),
    path('update-location/<pk>/', UpdateLocation.as_view()),
]