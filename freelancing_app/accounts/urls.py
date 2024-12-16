from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOutView.as_view(), name='logout'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='otp_verification'),
    path("resend-otp/", GenerateNewOTPView.as_view(), name='otp_resend'),  
    path("choose-role/", UserRoleRedirectView.as_view(), name="roles"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgotpassword"),
    path("reset-password/verify-otp/", PasswordResetOTPVerifyView.as_view(), name="verify-otp"),
    path("reset-password/resend-otp/", ForgotPasswordResendOTPView.as_view(), name="resendotp"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
