from django.urls import path
from .views import *

app_name = 'freelancer'

urlpatterns = [
    path('profile/', UserBasicInfoView.as_view(), name='profile'),
    path('edit-image/', EditProfileImageView.as_view(), name='edit-profile-image'),
    path('edit-info/', EditPersonalInfoView.as_view(), name='edit-personal-info'),
    path('edit-address/', EditUserAddressView.as_view(), name='edit-address'),
    path('edit-skill/', EditUserSkillsView.as_view(), name='edit-skill'),
    path('add-education/', AddEducationView.as_view(), name='add-new-education'),
    path('add-certificate/', AddCertificateView.as_view(), name='add-new-certificate'),
]