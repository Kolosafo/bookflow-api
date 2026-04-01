from django.urls import path
from .chat_ai.consumers import BookChatConsumer
from .summary_consumer import BookSummaryConsumer

websocket_urlpatterns = [
    path('chat/', BookChatConsumer.as_asgi()),
    path('summarize/', BookSummaryConsumer.as_asgi()),
]
