from django.urls import re_path
from . import consumers

# URLs des WebSockets
websocket_urlpatterns = [
    re_path(r'ws/vm_list/$', consumers.VMListConsumer.as_asgi()),
]