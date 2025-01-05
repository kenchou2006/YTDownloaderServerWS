import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from app import routings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routings.websocket_urlpatterns
        )
    ),
})
