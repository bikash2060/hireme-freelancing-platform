from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    # Home routes
    path('', HomeView.as_view(), name='home'),
    
    # List views
    path('freelancers/', FreelancerListView.as_view(), name='freelancers'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    
    # User profile
    path('profile/', GetUserProfileView.as_view(), name='user-profile'),
    
    # Project-related routes
    path('user-specific-project-list/', UserSpecificProjectListView.as_view(), name='user-specific-project-list'),
    path('project/<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail'),
]
