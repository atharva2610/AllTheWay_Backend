from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notification/<group_name>/', consumers.CustomerConsumer.as_asgi())
]