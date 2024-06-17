from django.db import models
from uuid import uuid4

class State(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['name']
    

class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['name']


class Location(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid4, editable = False)
    house_no = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    pincode = models.PositiveIntegerField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='location')
    is_deleted= models.BooleanField(default=False)

    def __str__(self):
        return f'{self.house_no}, {self.area}, {self.city.name}'
    
    @property
    def full_address(self):
        return f'{self.house_no}, {self.area}, {self.city.name} - {self.pincode}, {self.city.state.name}'