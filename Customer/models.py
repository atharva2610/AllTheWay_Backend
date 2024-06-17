from django.db import models
from Account.models import Account, DeliveryLocation
from Owner.models import MenuItem, Restaurant
from uuid import uuid4

order_status_option = {
    'ordered': 'Waiting for Restaurant to Accept.',
    'preparing': 'Restaurant is Preparing Order.',
    'prepared': 'Order is Ready for delivery.',
    'delivering': 'Rider is on the way to deliver.',
    'delivered': 'Order has been delivered.',
    'by_customer': 'Customer cancelled the Order.',
    'restaurant_rejected': 'Order cancelled! Restaurant rejected Order.',
    'out_of_stock': 'Order cancelled! Restaurant went Out Of Stock.',
    'accident': 'Order cancelled! Due to Accident.'
}

order_status_icon = {
    'ordered': 'pending_Actions',
    'preparing': 'skillet',
    'prepared': 'room_service',
    'delivering': 'directions_bike',
    'delivered': 'check_circle',
    'by_customer': 'cancel',
    'restaurant_rejected': 'cancel',
    'out_of_stock': 'cancel',
    'accident': 'cancel'
}

payment_modes_option = {
    'online': 'Payment via Online Mode',
    'cod': 'Payment via Cash (Cash On Delivery)'
}


class Order(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid4, editable = False)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_location = models.ForeignKey(DeliveryLocation, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=order_status_option, default='ordered')
    payment_mode = models.CharField(max_length=50, choices=payment_modes_option)
    item_amount = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    rated = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.name
    
    @property
    def restaurant_name(self):
        return self.restaurant.name
    
    @property
    def full_delivery_address(self):
        return self.delivery_location.location.full_address
    
    @property
    def status_text(self):
        return order_status_option.get(self.status)
    
    @property
    def status_icon(self):
        return order_status_icon.get(self.status)
    
    class Meta:
        ordering = ('-order_date',)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return str(self.order.id)
    
    @property
    def item_name(self):
        return self.item.name
    
    @property
    def is_veg(self):
        return self.item.is_veg
    

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    payment_id = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(default=0)
    isPaid = models.BooleanField(default=False)
    payment_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_id