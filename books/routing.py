from django.urls import path
from .chat_ai.consumers import BookChatConsumer

websocket_urlpatterns = [
    path('chat/', BookChatConsumer.as_asgi()),
]
