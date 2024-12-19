from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('basic-info/', UserBasicInfoView.as_view(), name='profile'),
    path('edit-profile-image/', EditProfileImageView.as_view(), name='edit'),
]
