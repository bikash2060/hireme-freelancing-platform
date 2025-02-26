from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signup/otp/', VerifyOTPView.as_view(), name='otp_verification'),
    path("signup/otp/resend/", GenerateNewOTPView.as_view(), name='otp_resend'),  
    path("signup/role/", UserRoleRedirectView.as_view(), name="roles"),
    path("password/reset/", ForgotPasswordView.as_view(), name="forgotpassword"),
    path("password/reset/otp/", PasswordResetOTPVerifyView.as_view(), name="verify-otp"),
    path("password/reset/otp/resend/", ForgotPasswordResendOTPView.as_view(), name="resendotp"),
    path("password/update/", ChangePasswordView.as_view(), name="change-password"),
]
