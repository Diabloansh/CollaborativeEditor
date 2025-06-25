from django.urls import re_path
from . import consumers

# WebSocket URL configuration
websocket_urlpatterns = [
    # WebSocket endpoint for real-time communication in the document editor
    # The `doc_id` is captured from the URL and passed to the DocumentConsumer
    re_path(r'ws/documents/(?P<doc_id>\d+)/$', consumers.DocumentConsumer.as_asgi()),
]


