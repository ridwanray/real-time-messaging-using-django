import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MessageNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['user_id']
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    
    async def chat_message(self, event):
        """Send message to receiver's room"""
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    async def chat_message_read(self, event):
        # Send a notification when a message is read
        message = event['message']
        await self.send(text_data=json.dumps({
            'message' : message
        }))