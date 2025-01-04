from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('client/', ClientDashboardView.as_view(), name='client'),
    path('freelancer/', FreelancerDashboardView.as_view(), name='freelancer'),
    path('proposals/<int:proposal_id>/send/', NewProposalsView.as_view(), name='send_proposal'),
]