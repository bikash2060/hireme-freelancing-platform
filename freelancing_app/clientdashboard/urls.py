from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('dashboard/', ClientDashboardView.as_view(), name='dashboard'),
    
]
