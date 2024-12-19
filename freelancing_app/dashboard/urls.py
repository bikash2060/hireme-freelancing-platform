from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('client/', ClientDashboardView.as_view(), name='client'),
    path('freelancer/', FreelancerDashboardView.as_view(), name='freelancer')
]