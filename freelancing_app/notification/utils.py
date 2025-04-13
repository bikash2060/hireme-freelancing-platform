# utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

class NotificationManager:
    @classmethod
    def send_notification(cls, user, message, redirect_url=None):
        """
        Send a real-time notification to a user
        
        Args:
            user: The recipient user instance
            message: Notification message content
            redirect_url: Optional URL to redirect user when clicking notification
        """
        notification = Notification.objects.create(
            user=user,
            message=message,
            redirect_url=redirect_url
        )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'send_notification',
                'message': message,
                'notification_id': notification.id,
                'redirect_url': redirect_url,
                'created_at': notification.created_at.isoformat(),
                'unread_count': Notification.objects.filter(user=user, is_read=False).count()
            }
        )