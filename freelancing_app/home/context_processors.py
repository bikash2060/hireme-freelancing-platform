from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        all_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
        unread_notifications = all_notifications.filter(is_read=False)
        unread_count = unread_notifications.count()

        return {
            'all_notifications': all_notifications,
            'unread_notifications': unread_notifications,
            'unread_count': unread_count
        }
    return {}