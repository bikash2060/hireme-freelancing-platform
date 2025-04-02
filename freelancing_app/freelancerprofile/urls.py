from django.urls import path
from .views import *

app_name = 'freelancer'

urlpatterns = [
    path('profile/', FreelancerBasicInfoView.as_view(), name='profile'),
    path('profile/info/', EditFreelancerPersonalInfoView.as_view(), name='edit-personal-info'),
    path('profile/image/delete/', DeleteProfileImageView.as_view(), name='delete-profile-image'),
    path('profile/skills/', EditFreelancerProfessionalInfoView.as_view(), name='edit-professional-info'),
    path('get-cities/', GetCitiesByCountryView.as_view(), name='get-cities'),
]