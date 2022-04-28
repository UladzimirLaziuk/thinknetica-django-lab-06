from django.urls import re_path

from shop_site import consumers

websocket_urlpatterns = [
    re_path(r'ws/bot/', consumers.EchoConsumerAsync.as_asgi()),
]
