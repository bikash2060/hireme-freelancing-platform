from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('index/',HomeView.as_view()),
    path('', HomeView.as_view(), name='home'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancers'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('profile/', GetUserProfileView.as_view(), name='user-profile'),
    path('user-specific-project-list/', UserSpecificProjectListView.as_view(), name='user-specific-project-list'),
    path('project/<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail'),
]
