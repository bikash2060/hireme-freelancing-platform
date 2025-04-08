from django.urls import path
from .views import *

app_name = 'freelancer'

urlpatterns = [
    path('profile/', FreelancerBasicInfoView.as_view(), name='profile'),
    path('profile/personalinfo/', EditFreelancerPersonalInfoView.as_view(), name='edit-personal-info'),
    path('profile/image/delete/', DeleteProfileImageView.as_view(), name='delete-profile-image'),
    path('profile/professionalinfo/', EditFreelancerProfessionalInfoView.as_view(), name='edit-professional-info'),
    path('profile/experience/add/', AddFreelancerExperienceView.as_view(), name='add-experience'),
    path('profile/experience/<int:experience_id>/edit/', EditFreelancerExperienceView.as_view(), name='edit-experience'),
    path('profile/experience/<int:experience_id>/delete/', DeleteFreelancerExperienceView.as_view(), name='delete-experience'),
    path('profile/education/add/', AddFreelancerEducationView.as_view(), name='add-education'),
    path('profile/education/<int:education_id>/edit/', EditFreelancerEducationView.as_view(), name='edit-education'),
    path('profile/education/<int:education_id>/delete/', DeleteFreelancerEducationView.as_view(), name='delete-education'), 
    path('profile/links/edit/', EditFreelancerLinksView.as_view(), name='edit-links'),     
    path('get-cities/', GetCitiesByCountryView.as_view(), name='get-cities'),
    path('password/change/', FreelancerPasswordChangeView.as_view(), name='change-password'),
]