import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from channels.auth import AuthMiddlewareStack
import Customer.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AllTheWay.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': OriginValidator(AuthMiddlewareStack(URLRouter(
        Customer.routing.websocket_urlpatterns
    )), ['https://alltheway.vercel.app'])
})
