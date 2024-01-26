"""
ASGI config for Messaging project.
"""

import os
from decouple import config
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from core.routing import websocket_urlpatterns
from messaging.middleware import CustomTokenAuthMiddleware

environment = config('ENVIRONMENT')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings."+environment)

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': CustomTokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})