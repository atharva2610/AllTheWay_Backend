from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Restaurant, Rating

@receiver(post_save, sender=Restaurant)
def create_rating(sender, instance, created, **kwargs):

    if created:
        Rating.objects.create(restaurant=instance)
