from django.contrib import admin
from .models import Restaurant, Rating, Cuisine, MenuItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    model = Restaurant
    list_display = ['name', 'owner']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    model = Rating


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    model = Cuisine
    list_display = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    model = MenuItem
    list_display = ['name', 'restaurant']