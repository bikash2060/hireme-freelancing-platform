from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("verify-otp/", VerifyOTPView.as_view(), name="otp_verification"),
    path("resend-otp/", ResendOTPView.as_view(), name='otp_resend'),  
    path("choose-role/", UserRoleRedirectView.as_view(), name="roles"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgotpassword"),
    path("password-reset/", PasswordResetView.as_view(), name="resetpassword"),
    path("resend-otp/", ForgotPasswordResendOTPView.as_view(), name="resendotp"),
    path("change-password/", ChangePasswordView.as_view(), name="changepassword"),
]
