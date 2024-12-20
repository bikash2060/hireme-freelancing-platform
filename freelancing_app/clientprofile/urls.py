from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('profile/', UserBasicInfoView.as_view(), name='profile'),
    path('edit-profile-image/', EditProfileImageView.as_view(), name='edit-profile-image'),
    path('edit-personal-info/', EditPersonalInfoView.as_view(), name='edit-personal-info'),
]
