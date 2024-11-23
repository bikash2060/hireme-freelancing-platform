from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("verify/", views.verify_otp, name="verifyotp"),
    path("career/",views.user_redirect, name="user-redirect" )
]