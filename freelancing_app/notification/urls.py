from django.urls import path
from .views import *

app_name = 'notification'

urlpatterns = [
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark_all_read'),
    path('mark-read/<int:notification_id>/', MarkAsReadView.as_view(), name='mark_as_read'),
    path('get-notifications/', GetNotificationsView.as_view(), name='get_notifications'),
] 