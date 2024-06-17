from django.contrib import admin
from .models import Order, OrderItem, OrderPayment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ['customer', 'restaurant']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem
    list_display = ['order', 'item', 'quantity']


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    model = OrderPayment
    list_display = ['order', 'amount', 'isPaid']
