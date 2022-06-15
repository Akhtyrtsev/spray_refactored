from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from spray.chat.routing import websocket_urlpatterns
from spray.chat.middlewares import TokenAuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        'websocket': TokenAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)
