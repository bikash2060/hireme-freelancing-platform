from accounts.mixins import CustomLoginRequiredMixin
from django.http import JsonResponse
from .models import Notification
from django.views import View

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseNotificationView
# Description: Base class for notification-related views with utility methods
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseNotificationView(CustomLoginRequiredMixin, View):
    """
    Base class for notification-related views. Provides utility methods.
    Ensures requests are AJAX for notification modifications.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the request is AJAX for notification modification endpoints.
        """
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request'}, status=400)
        return super().dispatch(request, *args, **kwargs)

    def get_notification(self, notification_id, user):
        """
        Get notification instance with validation.
        Returns notification or None if not found.
        """
        try:
            return Notification.objects.get(id=notification_id, user=user)
        except Notification.DoesNotExist:
            return None

    def get_unread_count(self, user):
        """
        Get count of unread notifications for the user.
        """
        return Notification.objects.filter(user=user, is_read=False).count()

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: MarkAsReadView
# Description: Marks a single notification as read for the authenticated user
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class MarkAsReadView(BaseNotificationView):
    """
    - Marks a specific notification as read
    - Returns updated unread notification count
    - Requires AJAX request and valid notification ID
    """

    def post(self, request, notification_id):
        try:
            notification = self.get_notification(notification_id, request.user)
            if not notification:
                return JsonResponse({
                    'success': False,
                    'error': 'Notification not found'
                }, status=404)

            notification.is_read = True
            notification.save()
            
            return JsonResponse({
                'success': True,
                'unread_count': self.get_unread_count(request.user)
            })

        except Exception as e:
            print(f"[MarkAsReadView Error]: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Server error occurred'
            }, status=500)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: MarkAllReadView
# Description: Marks all notifications as read for the authenticated user
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class MarkAllReadView(BaseNotificationView):
    """
    - Marks all notifications as read for the current user
    - Returns success status with unread count (0)
    - Requires AJAX request
    """

    def post(self, request):
        try:
            Notification.objects.filter(user=request.user).update(is_read=True)
            return JsonResponse({
                'success': True,
                'unread_count': 0
            })

        except Exception as e:
            print(f"[MarkAllReadView Error]: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Server error occurred'
            }, status=500)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: GetNotificationsView
# Description: Retrieves recent notifications for the authenticated user
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class GetNotificationsView(View):
    """
    - Retrieves the 10 most recent notifications for the user
    - Includes unread count
    - Works for both authenticated and unauthenticated users
    """

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    'notifications': [],
                    'unread_count': 0
                })

            notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]

            unread_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()

            notifications_data = [{
                'id': notification.id,
                'message': notification.message,
                'is_read': notification.is_read,
                'redirect_url': notification.redirect_url,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for notification in notifications]

            return JsonResponse({
                'notifications': notifications_data,
                'unread_count': unread_count
            })

        except Exception as e:
            print(f"[GetNotificationsView Error]: {e}")
            return JsonResponse({
                'notifications': [],
                'unread_count': 0
            })