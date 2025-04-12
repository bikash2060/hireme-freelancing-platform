# utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

class NotificationManager:
    @classmethod
    def send_notification(cls, user, message, notification_type, related_id=None):
        """
        Send a real-time notification to a user
        
        Args:
            user: The recipient user instance
            message: Notification message content
            notification_type: Type/category of notification
            related_id: Optional ID of related object
        """
        notification = Notification.objects.create(
            user=user,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'send_notification',
                'message': message,
                'notification_id': notification.id,
                'notification_type': notification_type,
                'related_id': related_id,
                'created_at': notification.created_at.isoformat(),
                'unread_count': Notification.objects.filter(user=user, is_read=False).count()
            }
        )