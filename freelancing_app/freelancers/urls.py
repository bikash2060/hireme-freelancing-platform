from django.urls import path
from .views import *

app_name = 'freelancers'

urlpatterns = [
   path('', FreelancerListView.as_view(), name='freelancer-list'),
]