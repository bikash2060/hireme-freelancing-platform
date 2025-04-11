from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    # Authentication paths
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Registration paths
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signup/verify-otp/', VerifyOTPView.as_view(), name='otp_verification'),
    path('signup/resend-otp/', GenerateNewOTPView.as_view(), name='otp_resend'),  
    path('signup/select-role/', UserRoleRedirectView.as_view(), name="roles"),
    
    # Password reset paths
    path('reset-password/', ForgotPasswordView.as_view(), name="forgotpassword"),
    path('reset-password/verify/', PasswordResetOTPVerifyView.as_view(), name="verify-otp"),
    path('reset-password/resend-code/', ForgotPasswordResendOTPView.as_view(), name="resendotp"),
    path('reset-password/confirm/', ChangePasswordView.as_view(), name="change-password"),
    
    # OAuth paths
    path('oauth/select-role/', OAuthRoleSelectionView.as_view(), name="oauth_role_selection"),
]
