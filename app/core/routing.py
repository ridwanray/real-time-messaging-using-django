from django.urls import path
from messaging.consumer import MessageNotificationConsumer

websocket_urlpatterns = [
    path('messaging/', MessageNotificationConsumer.as_asgi()),
]