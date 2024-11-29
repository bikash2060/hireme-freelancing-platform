from django.urls import path
from . import views

app_name = 'accounts'  

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("otp/verification/", views.verify_otp, name="otp_verification"),
    path("career/", views.user_redirect, name="user-redirect"),
]
