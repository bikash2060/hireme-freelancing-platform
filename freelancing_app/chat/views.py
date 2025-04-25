from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from .models import ChatRoom

User = get_user_model()

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ChatListView
# Description: Returns chat list with existing and potential chats
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refactor Status: Completed
# ------------------------------------------------------
class ChatListView(CustomLoginRequiredMixin, View):
    """Returns all chats: both existing and potential (new)"""

    def get(self, request):
        try:
            existing_chats = self._get_existing_chats(request)
            potential_chats = self._get_potential_chats(request, existing_chats)

            all_chats = existing_chats + potential_chats
            return JsonResponse({'chats': all_chats})
        except Exception as e:
            print(f"[ChatListView Error] {e}")
            return JsonResponse({'error': 'Unable to fetch chat list'}, status=500)

    def _get_existing_chats(self, request):
        chats = []
        for room in request.user.chat_rooms.all():
            other_user = room.participants.exclude(id=request.user.id).first()
            last_msg = room.messages.last()
            chats.append({
                'room_name': room.name,
                'other_user': self._serialize_user(other_user),
                'last_message': self._serialize_last_message(last_msg, request),
                'unread_count': room.messages.filter(read=False).exclude(sender=request.user).count(),
                'is_existing': True,
                'last_activity': last_msg.timestamp if last_msg else None
            })
        return sorted(chats, key=lambda x: (x['last_activity'] or timezone.datetime.min).replace(tzinfo=None), reverse=True)

    def _get_potential_chats(self, request, existing_chats):
        existing_ids = [chat['other_user']['id'] for chat in existing_chats]
        potential = []
        for user in User.objects.exclude(id=request.user.id).exclude(id__in=existing_ids).exclude(is_superuser=True):
            potential.append({
                'room_name': None,
                'other_user': self._serialize_user(user),
                'last_message': None,
                'unread_count': 0,
                'is_existing': False,
                'last_activity': None
            })
        return potential

    def _serialize_user(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name or user.username,
            'profile_image': f"/media/profile_images/{user.profile_image}" if user.profile_image else None,
            'is_online': self._is_online(user),
        }

    def _serialize_last_message(self, message, request):
        if not message:
            return None
        return {
            'content': message.content,
            'timestamp': message.timestamp,
            'sender': 'You' if message.sender == request.user else None
        }

    def _is_online(self, user):
        return hasattr(user, 'last_activity') and user.last_activity and (timezone.now() - user.last_activity).seconds < 300


# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ChatMessagesView
# Description: Returns messages for a chat room
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refactor Status: Completed
# ------------------------------------------------------
class ChatMessagesView(CustomLoginRequiredMixin, View):
    """Returns chat messages for a specific chat room"""

    def get(self, request, room_name):
        try:
            room = get_object_or_404(ChatRoom, name=room_name)
            if request.user not in room.participants.all():
                return JsonResponse({'error': 'Not authorized'}, status=403)

            messages = room.messages.all().order_by('timestamp')
            data = [self._serialize_message(m, request) for m in messages]

            room.messages.filter(read=False).exclude(sender=request.user).update(read=True)
            return JsonResponse({'messages': data})
        except Exception as e:
            print(f"[ChatMessagesView Error] {e}")
            return JsonResponse({'error': 'Failed to fetch messages'}, status=500)

    def _serialize_message(self, message, request):
        return {
            'id': message.id,
            'sender': {
                'id': message.sender.id,
                'username': message.sender.username,
                'profile_image': f"/media/profile_images/{message.sender.profile_image}" if message.sender.profile_image else None,
            },
            'content': message.content,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M"),
            'is_sent': message.sender == request.user,
        }


# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: StartChatView
# Description: Starts a new chat or retrieves an existing one
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refactor Status: Completed
# ------------------------------------------------------
class StartChatView(CustomLoginRequiredMixin, View):
    """Initiates or retrieves a one-on-one chat room"""

    def post(self, request, user_id):
        try:
            other_user = get_object_or_404(User, id=user_id)
            if other_user == request.user:
                return JsonResponse({'error': 'Cannot chat with yourself'}, status=400)

            room_name = self._generate_room_name(request.user.id, other_user.id)
            room, _ = ChatRoom.objects.get_or_create(name=room_name)
            room.participants.add(request.user, other_user)

            return JsonResponse({
                'room_name': room_name,
                'other_user': self._serialize_user(other_user)
            })
        except Exception as e:
            print(f"[StartChatView Error] {e}")
            return JsonResponse({'error': 'Unable to start chat'}, status=500)

    def _generate_room_name(self, id1, id2):
        ids = sorted([id1, id2])
        return f"chat_{ids[0]}_{ids[1]}"

    def _serialize_user(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name or user.username,
            'profile_image': f"/media/profile_images/{user.profile_image}" if user.profile_image else None,
            'is_online': hasattr(user, 'is_online') and user.is_online
        }
