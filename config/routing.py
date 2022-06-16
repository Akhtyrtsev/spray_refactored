from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import spray.chat.routing
from spray.chat.middlewares import TokenAuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        'websocket': TokenAuthMiddlewareStack(
            URLRouter(
                spray.chat.routing.websocket_urlpatterns
            )
        ),
    }
)
