from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View
from .models import ChatRoom

User = get_user_model()

class ChatListView(CustomLoginRequiredMixin, View):
    def get(self, request):
        chat_rooms = request.user.chat_rooms.all()
        chats = []
        for room in chat_rooms:
            other_user = room.participants.exclude(id=request.user.id).first()
            last_message = room.messages.last()
            profile_image = f"/media/profile_images/{other_user.profile_image}" if other_user.profile_image else None
            chats.append({
                'room_name': room.name,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'full_name': other_user.full_name or other_user.username,
                    'profile_image': profile_image,
                },
                'last_message': {
                    'content': last_message.content if last_message else None,
                    'timestamp': last_message.timestamp if last_message else None,
                    'sender': last_message.sender.username if last_message else None,
                },
                'unread_count': room.messages.filter(read=False).exclude(sender=request.user).count(),
            })
        print(chats)
        return JsonResponse({'chats': chats})

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
        user_ids = sorted([request.user.id, other_user.id])
        room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        
        if request.user not in room.participants.all():
            room.participants.add(request.user)
        if other_user not in room.participants.all():
            room.participants.add(other_user)
        
        profile_image = f"/media/profile_images/{other_user.profile_image}" if other_user.profile_image else None
        return JsonResponse({
            'room_name': room_name,
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'profile_image': profile_image,
            }
        })