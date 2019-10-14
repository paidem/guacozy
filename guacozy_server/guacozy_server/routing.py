from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from .guacdproxy import GuacamoleConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('tunnelws/ticket/<uuid:ticket>/', GuacamoleConsumer),
        ])
    ),
})
