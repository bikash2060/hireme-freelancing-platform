from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('my-profile/', ClientProfileView.as_view(), name='profile'),
    path('my-profile/personal-info/', PersonalInfoView.as_view(), name='edit-personal-info'),
    path('my-profile/remove-image/', DeleteProfileImageView.as_view(), name='delete-profile-image'),    
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),    
    path('locations/cities/', GetCitiesByCountryView.as_view(), name='get-cities'),
    path('transactions/', ClientTransactionsView.as_view(), name='transactions'),
]