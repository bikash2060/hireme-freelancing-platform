from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('profile/', UserBasicInfoView.as_view(), name='profile'),
    path('profile/image/', EditProfileImageView.as_view(), name='edit-profile-image'),
    path('profile/info/', EditPersonalInfoView.as_view(), name='edit-personal-info'),
    path('profile/address/', EditUserAddressView.as_view(), name='edit-address'),
    path('profile/company/add/', AddCompanyView.as_view(), name='addcompany'),
    path('profile/company/<int:company_id>/edit/', EditCompanyView.as_view(), name='editcompany'),
    path('profile/company/<int:company_id>/delete', DeleteCompanyView.as_view(), name='delete-company'),
    path('profile/password/', PasswordChangeView.as_view(), name='change-password'),
]
