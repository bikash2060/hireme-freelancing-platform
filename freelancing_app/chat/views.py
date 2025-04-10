from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View
from .models import ChatRoom
from django.utils import timezone

User = get_user_model()

class ChatListView(CustomLoginRequiredMixin, View):
    def get(self, request):
        # Get existing chat rooms
        chat_rooms = request.user.chat_rooms.all()
        existing_chats = []
        
        for room in chat_rooms:
            other_user = room.participants.exclude(id=request.user.id).first()
            last_message = room.messages.last()
            profile_image = f"/media/profile_images/{other_user.profile_image}" if other_user.profile_image else None
            
            # Check if user is online (has been active in the last 5 minutes)
            is_online = False
            if hasattr(other_user, 'last_activity'):
                is_online = other_user.last_activity and (timezone.now() - other_user.last_activity).seconds < 300
            
            existing_chats.append({
                'room_name': room.name,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'full_name': other_user.full_name or other_user.username,
                    'profile_image': profile_image,
                    'is_online': is_online
                },
                'last_message': {
                    'content': last_message.content if last_message else None,
                    'timestamp': last_message.timestamp if last_message else None,
                    'sender': 'You' if last_message and last_message.sender == request.user else None,
                },
                'unread_count': room.messages.filter(read=False).exclude(sender=request.user).count(),
                'is_existing': True,
                'last_activity': last_message.timestamp if last_message else None
            })
        
        # Sort existing chats by last message timestamp (most recent first)
        existing_chats.sort(key=lambda x: (x['last_activity'] or timezone.datetime.min).replace(tzinfo=None), reverse=True)
        
        # Get all other users who don't have chats yet
        existing_user_ids = [chat['other_user']['id'] for chat in existing_chats]
        other_users = User.objects.exclude(id=request.user.id).exclude(id__in=existing_user_ids).exclude(is_superuser=True)
        
        potential_chats = []
        for user in other_users:
            profile_image = f"/media/profile_images/{user.profile_image}" if user.profile_image else None
            
            # Check if user is online (has been active in the last 5 minutes)
            is_online = False
            if hasattr(user, 'last_activity'):
                is_online = user.last_activity and (timezone.now() - user.last_activity).seconds < 300
            
            potential_chats.append({
                'room_name': None,  # No room exists yet
                'other_user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name or user.username,
                    'profile_image': profile_image,
                    'is_online': is_online
                },
                'last_message': None,
                'unread_count': 0,
                'is_existing': False,
                'last_activity': None
            })
        
        # Combine existing and potential chats
        all_chats = existing_chats + potential_chats
        
        return JsonResponse({'chats': all_chats})

class ChatMessagesView(CustomLoginRequiredMixin, View):
    def get(self, request, room_name):
        room = get_object_or_404(ChatRoom, name=room_name)
        if request.user not in room.participants.all():
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        messages = room.messages.all().order_by('timestamp')
        messages_data = []
        for message in messages:
            profile_image = f"/media/profile_images/{message.sender.profile_image}" if message.sender.profile_image else None
            messages_data.append({
                'id': message.id,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'profile_image': profile_image,
                },
                'content': message.content,
                'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M"),
                'is_sent': message.sender == request.user,
            })
        
        room.messages.filter(read=False).exclude(sender=request.user).update(read=True)
        return JsonResponse({'messages': messages_data})

class StartChatView(CustomLoginRequiredMixin, View):
    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        
        # Prevent users from chatting with themselves
        if other_user == request.user:
            return JsonResponse({'error': 'Cannot chat with yourself'}, status=400)
        
        # Create consistent room name by sorting user IDs
        user_ids = sorted([request.user.id, other_user.id])
        room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        # Get or create the chat room
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        
        # Add participants if they're not already in the room
        if request.user not in room.participants.all():
            room.participants.add(request.user)
        if other_user not in room.participants.all():
            room.participants.add(other_user)
        
        profile_image = f"/media/profile_images/{other_user.profile_image}" if other_user.profile_image else None
        
        # Check if user is online
        is_online = other_user.is_online if hasattr(other_user, 'is_online') else False
        
        return JsonResponse({
            'room_name': room_name,
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'full_name': other_user.full_name or other_user.username,
                'profile_image': profile_image,
                'is_online': is_online
            }
        })