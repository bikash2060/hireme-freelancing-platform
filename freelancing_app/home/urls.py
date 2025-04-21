from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancers'),
    path('freelancer/<int:freelancer_id>/detail/', FreelancerDetailView.as_view(), name='freelancer-detail'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('user-specific-project-list/', UserSpecificProjectListView.as_view(), name='user-specific-project-list'),
    path('project/<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail'),
    path('profile/', GetUserProfileView.as_view(), name='user-profile'), 
]
