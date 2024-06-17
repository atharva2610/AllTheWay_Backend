from django.contrib import admin
from .models import Account, DeliveryLocation

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ['email', 'name']


@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    model = DeliveryLocation
    list_display = ['user', 'location']