# urls.py
from django.urls import path
from .views import *

app_name = 'freelancer'

urlpatterns = [
    # Profile views
    path('my-profile/', FreelancerProfileView.as_view(), name='profile'),
    path('my-profile/personal-info/', PersonalInfoView.as_view(), name='edit-personal-info'),
    path('my-profile/remove-image/', DeleteProfileImageView.as_view(), name='delete-profile-image'),
    path('my-profile/professional-info/', ProfessionalInfoView.as_view(), name='edit-professional-info'),
    
    # Experience views
    path('my-profile/experience/new/', AddExperienceView.as_view(), name='add-experience'),
    path('my-profile/experience/<int:experience_id>/edit/', EditExperienceView.as_view(), name='edit-experience'),
    path('my-profile/experience/<int:experience_id>/delete/', DeleteExperienceView.as_view(), name='delete-experience'),
    
    # Education views
    path('my-profile/education/new/', AddEducationView.as_view(), name='add-education'),
    path('my-profile/education/<int:education_id>/edit/', EditEducationView.as_view(), name='edit-education'),
    path('my-profile/education/<int:education_id>/delete/', DeleteEducationView.as_view(), name='delete-education'),
    
    # Other profile sections
    path('my-profile/links/', EditLinksView.as_view(), name='edit-links'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # Utilities
    path('locations/cities/', GetCitiesByCountryView.as_view(), name='get-cities'),
]