from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('profile/', ClientBasicInfoView.as_view(), name='profile'),
    path('profile/personalinfo/', EditFreelancerPersonalInfoView.as_view(), name='edit-personal-info'),
    path('profile/image/delete/', DeleteProfileImageView.as_view(), name='delete-profile-image'),
    path('get-cities/', GetCitiesByCountryView.as_view(), name='get-cities'),
    path('password/change/', ClientChangePasswordView.as_view(), name='change-password'),

]
