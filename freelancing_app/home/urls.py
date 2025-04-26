from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancers'),
    path('freelancer/<int:freelancer_id>/detail/', FreelancerDetailView.as_view(), name='freelancer-detail'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('project/<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail'),
    path('profile/', GetUserProfileView.as_view(), name='user-profile'),
    path('about-us/', AboutUsView.as_view(), name='about-us'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
]
