from django.urls import path
from .views import *

app_name = 'freelancer'

urlpatterns = [
    path('profile/', UserBasicInfoView.as_view(), name='profile'),
    path('profile/image/', EditProfileImageView.as_view(), name='edit-profile-image'),
    path('profile/info/', EditPersonalInfoView.as_view(), name='edit-personal-info'),
    path('profile/address/', EditUserAddressView.as_view(), name='edit-address'),
    path('profile/skill/', EditUserSkillsView.as_view(), name='edit-skill'),
    path('profile/education/add/', AddEducationView.as_view(), name='add-new-education'),
    path('profile/education/<int:education_id>/edit/', EditEducationView.as_view(), name='edit-education'),
    path('profile/education/<int:education_id>/delete/', DeleteEducationView.as_view(), name='delete-education'),
    path('profile/certificate/add/', AddCertificateView.as_view(), name='add-new-certificate'),
    path('profile/certificate/<int:certificate_id>/edit/', EditCertificateView.as_view(), name='edit-certificate'),
    path('profile/certificate/<int:certificate_id>/delete', DeleteCertificateView.as_view(), name='delete-certificate'),
    path('profile/password/', PasswordChangeView.as_view(), name='change-password'),
]