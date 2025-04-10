from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, ChatRoom
from asgiref.sync import sync_to_async
from accounts.models import User
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Broadcast user's online status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'status_change',
                'user_id': self.user.id,
                'is_online': True
            }
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Broadcast user's offline status before leaving
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'status_change',
                'user_id': self.user.id,
                'is_online': False
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if text_data_json.get('type') == 'typing':
            # Handle typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'sender': self.user.id
                }
            )
        else:
            # Handle regular message
            message = text_data_json['message']
            sender = self.user.id
            
            # Save message to database
            await self.save_message(self.room_name, sender, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender']
        }))

    async def status_change(self, event):
        # Send status change to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status_change',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))
    
    @sync_to_async
    def save_message(self, room_name, sender_id, message):
        room = ChatRoom.objects.get(name=room_name)
        sender = User.objects.get(id=sender_id)
        ChatMessage.objects.create(room=room, sender=sender, content=message)