from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("otp/verification/", VerifyOTPView.as_view(), name="otp_verification"),
    path('otp_resend/', ResendOTPView.as_view(), name='otp_resend'),  
    path("role/", UserRoleRedirectView.as_view(), name="roles"),
]
