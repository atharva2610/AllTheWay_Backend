from django.contrib import admin
from .models import State, City, Location

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    model = State
    list_display = ['name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name', 'state']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    model = Location