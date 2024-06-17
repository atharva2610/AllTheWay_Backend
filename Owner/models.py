from django.db import models
from uuid import uuid4
from django.core.exceptions import ValidationError
from Account.models import Account
from Address.models import Location
from cloud_storages.backends.appwrite import AppWriteStorage


custom_storage = AppWriteStorage()

def phoneNoLength(phone):
    if len(str(phone)) != 10:
        raise ValidationError('Phone No. should have 10 digits.')
    
    
class Restaurant(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid4, editable = False)
    name = models.CharField(max_length=50)
    license = models.CharField(max_length=50)
    phone = models.PositiveBigIntegerField(verbose_name='phone no.', validators=[phoneNoLength])
    image = models.ImageField(storage=custom_storage, blank=True, null=True, default='restaurant.jpg')
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='restaurant')
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='restaurant')
    veg = models.BooleanField(default=True)
    temporary_close = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def toggle_temporary_close(self):
        self.temporary_close = not self.temporary_close
        self.save()

    def __str__(self):
        return self.name


class Rating(models.Model):
    total_rating = models.PositiveSmallIntegerField(default=0)
    no_of_ratings = models.PositiveSmallIntegerField(default=0)
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='rating')

    def __str__(self):
        return self.restaurant.name

    @property
    def average_rating(self):
        if (self.no_of_ratings == 0):
            return 0
        return f"{self.total_rating/self.no_of_ratings:.1f}"
    

class Cuisine(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(storage=custom_storage, blank=True, null=True, default='defaultItemImage.jpeg')
    is_veg = models.BooleanField(default=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, related_name='menuitem')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menuitem')
    is_deleted= models.BooleanField(default=False)

    def __str__(self):
        return self.name