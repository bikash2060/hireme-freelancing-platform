from django.urls import path
from .views import *

app_name = 'homes'

urlpatterns = [
    path('index/',HomeView.as_view()),
    path('', HomeView.as_view(), name='home'),
    path('freelancers/', FreelancersView.as_view(), name='freelancers'),
    path('projects/', ProjectsView.as_view(), name='projects'),    
]
