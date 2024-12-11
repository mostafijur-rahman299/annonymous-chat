# This file coding sequence can't be changed it must be avoid prettifier 
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whato.settings.base")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from .routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(websocket_urlpatterns)
    }
)
