from django.urls import path
from .views import *
app_name = 'chat'

urlpatterns = [
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/<str:room_name>/', ChatMessagesView.as_view(), name='chat_messages'),
    path('start-chat/<int:user_id>/', StartChatView.as_view(), name='start_chat'),
]