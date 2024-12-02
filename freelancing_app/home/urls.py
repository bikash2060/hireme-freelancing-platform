from django.urls import path
from .views import *

app_name = 'homes'

urlpatterns = [
    path('index/',HomeView.as_view()),
    path('', HomeView.as_view(), name='home'),
]
