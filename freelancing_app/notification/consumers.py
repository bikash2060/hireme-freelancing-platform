# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'] == AnonymousUser():
            await self.close()
        else:
            self.user = self.scope['user']
            self.group_name = f'user_{self.user.id}'
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_as_read':
            await self.mark_notification_as_read(data['notification_id'])

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        Notification.objects.filter(id=notification_id, user=self.user).update(is_read=True)
