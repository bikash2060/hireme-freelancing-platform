from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat.routing
import notification.routing
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelancing_app.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns + 
            notification.routing.websocket_urlpatterns
        )
    ),
})