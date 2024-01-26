from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message


@receiver(post_save, sender=Message)
def broadcast_new_message(sender, instance: Message, created, **kwargs):
    """Broadcast new message to the receiver's room"""
    if created:
        
        new_message = {
            "type": "new_message",
            "sender": str(instance.sender.id),
            "content": instance.content,
            "time": str(instance.created_at),
            "message_id": str(instance.id),
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(instance.receiver.id),
            {
                "type": "chat.message",
                "message": new_message,
            },
        )


@receiver(post_save, sender=Message)
def send_read_message_notification(sender, instance, created, **kwargs):
    """Send message read notification to the sender's room"""
    if not created and instance.is_read:
        
        channel_layer = get_channel_layer()
        group_name = f"{instance.sender.id}"
        data = {
            "type": "message_read_status",
            "message_id": str(instance.id),
            "sender": str(instance.sender.id),
            "read_at": str(datetime.now()),
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat.message_read",
                "message": data,
            },
        )