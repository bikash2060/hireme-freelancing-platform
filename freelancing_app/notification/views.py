from accounts.mixins import CustomLoginRequiredMixin
from django.http import JsonResponse
from .models import Notification
from django.views import View

class MarkAsReadView(CustomLoginRequiredMixin, View):
    def post(self, request, notification_id):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                notification = Notification.objects.get(id=notification_id, user=request.user)
                notification.is_read = True
                notification.save()
                
                unread_count = Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).count()
                
                return JsonResponse({
                    'success': True,
                    'unread_count': unread_count
                })
            except Notification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Notification not found'
                }, status=404)
        return JsonResponse({'error': 'Invalid request'}, status=400)

class MarkAllReadView(CustomLoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            Notification.objects.filter(user=request.user).update(is_read=True)
            return JsonResponse({
                'success': True,
                'unread_count': 0
            })
        return JsonResponse({'error': 'Invalid request'}, status=400)

class GetNotificationsView(View):
    def get(self, request):
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
