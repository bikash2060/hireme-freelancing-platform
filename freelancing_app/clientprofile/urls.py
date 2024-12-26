from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('profile/', UserBasicInfoView.as_view(), name='profile'),
    path('edit-image/', EditProfileImageView.as_view(), name='edit-profile-image'),
    path('edit-info/', EditPersonalInfoView.as_view(), name='edit-personal-info'),
    path('edit-address/', EditUserAddressView.as_view(), name='edit-address'),
    path('add-company/', AddCompanyView.as_view(), name='addcompany'),
]
