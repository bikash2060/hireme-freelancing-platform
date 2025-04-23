from allauth.socialaccount.models import SocialLogin, SocialAccount
from django.contrib.auth import login, authenticate, logout
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from freelancerprofile.models import Freelancer
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from clientprofile.models import Client
from django.contrib import messages
from smtplib import SMTPException
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.views import View
from .formvalidation import *
from .models import *
from .utils import *
import requests
import uuid
import os

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseAuthView
# Description: Base view for authentication-related views with common properties
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseAuthView(View):
    """Base view for authentication-related views with common properties"""
    login_url = 'account:login'
    home_url = 'home:home'
    signup_url = 'account:signup'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user is already authenticated"""
        if request.user.is_authenticated:
            return redirect(self.home_url)
        return super().dispatch(request, *args, **kwargs)
    
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: UserLoginView
# Description: Handles user authentication via email/password
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class UserLoginView(BaseAuthView):
    """
    - Handles traditional email/password login
    - Validates input, checks for OAuth conflicts
    - Authenticates and redirects user on success
    """
    TEMPLATE_NAME = 'accounts/login.html'

    def get(self, request):
        """Display login form"""
        return self._render_login_form(request)

    def post(self, request):
        """Handle login submission"""
        return self._process_login(request)

    def _render_login_form(self, request, form_data=None):
        try:
            return render(request, self.TEMPLATE_NAME, {'form_data': form_data or {}})
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def _process_login(self, request):
        try:
            email = request.POST.get('emailaddress', '').strip().lower()
            password = request.POST.get('password', '').strip()
            form_data = {'email': email}

            # Validate form input
            valid, error_message = FormValidator.validate_login(email, password)
            if not valid:
                messages.error(request, error_message)
                return self._render_login_form(request, form_data)

            # Handle Google-registered users
            if User.objects.filter(email=email, auth_method='google').exists():
                messages.error(request, 'This email is registered with Google. Please login with Google.')
                return self._render_login_form(request, form_data)

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect(self.home_url)

            # Handle login failure
            return self._handle_failed_login(request, email, form_data)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _handle_failed_login(self, request, email, form_data):
        """Display appropriate error for login failure"""
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Incorrect password. Please try again.')
        else:
            messages.error(request, 'Invalid email or password.')
        return self._render_login_form(request, form_data)
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ForgotPasswordView
# Description: Handles password reset requests
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------      
class ForgotPasswordView(BaseAuthView):
    """
    - Handles password reset requests via email
    - Validates email and prevents reset for Google-authenticated users
    - Generates and sends OTP for password reset
    """
    TEMPLATE_NAME = 'accounts/reset_password_request.html'
    OTP_VERIFICATION_URL = 'account:verify-otp'

    def get(self, request):
        """Render password reset request form"""
        return self._render_reset_form(request)

    def post(self, request):
        """Handle form submission for password reset request"""
        return self._handle_password_reset_request(request)

    def _render_reset_form(self, request):
        try:
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _handle_password_reset_request(self, request):
        try:
            email = request.POST.get('email', '').strip().lower()

            if not email:
                messages.error(request, 'Please enter your email address.')
                return self._render_reset_form(request)

            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
                return self._render_reset_form(request)

            # Prevent reset for Google-authenticated users
            if user.auth_method == 'google':
                messages.error(request, 'This email is registered with Google. Please login using Google.')
                return self._render_reset_form(request)

            # Generate and send OTP
            self._generate_and_send_otp(email)

            # Save email in session
            request.session['email_address'] = email
            request.session.set_expiry(timedelta(minutes=10))

            messages.success(request, 'An OTP has been sent to your email address.')
            return redirect(self.OTP_VERIFICATION_URL)

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return self._render_reset_form(request)
        except Exception as e:
            print(f"[ForgotPassword Error] {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _generate_and_send_otp(self, email):
        """Delete previous OTPs, generate and send a new one"""
        OTPCode.objects.filter(email=email).delete()
        otp_code = OTPService.generate_and_save_otp(email)
        EmailService.send_reset_password_email(email, otp_code)
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PasswordResetOTPVerifyView
# Description: Handles OTP verification for password reset
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PasswordResetOTPVerifyView(BaseAuthView):
    """
    - Verifies OTP for password reset
    - Ensures session and OTP validity
    - Redirects to password change form if OTP is valid
    """
    TEMPLATE_NAME = 'accounts/reset_password_otp_verification.html'
    RESET_REQUEST_URL = 'account:forgotpassword'
    PASSWORD_RESET_URL = 'account:change-password'

    def get(self, request):
        """Display OTP verification form"""
        return self._render_otp_form(request)

    def post(self, request):
        """Verify submitted OTP and redirect if successful"""
        return self._verify_otp(request)

    def _render_otp_form(self, request):
        try:
            if not request.session.get('email_address'):
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.RESET_REQUEST_URL)
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

    def _verify_otp(self, request):
        try:
            email = request.session.get('email_address')
            if not email:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.RESET_REQUEST_URL)

            otp_entered = self._get_otp_from_request(request)
            if not otp_entered or len(otp_entered) != 6:
                messages.error(request, 'Please enter a valid 6-digit OTP.')
                return self._render_otp_form(request)

            otp_record = OTPCode.objects.get(email=email)

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP expired. Please request a new one.')
                return self._render_otp_form(request)

            if otp_entered != str(otp_record.otp_code):
                messages.error(request, 'Invalid OTP. Please try again.')
                return self._render_otp_form(request)

            otp_record.is_verified = True
            otp_record.save()
            messages.success(request, 'OTP verified successfully.')
            return redirect(self.PASSWORD_RESET_URL)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return self._render_otp_form(request)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

    def _get_otp_from_request(self, request):
        """Helper to extract 6-digit OTP from request"""
        return ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ForgotPasswordResendOTPView
# Description: Handles OTP resend for password reset
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------      
class ForgotPasswordResendOTPView(BaseAuthView):
    """
    - Handles resending OTP during password reset flow
    - Requires active session with email
    """
    TEMPLATE_NAME = 'accounts/reset_password_otp_verification.html'
    RESET_REQUEST_URL = 'account:forgotpassword'

    def get(self, request):
        """Resend OTP if session is valid"""
        return self._resend_otp(request)

    def _resend_otp(self, request):
        try:
            email = request.session.get('email_address')
            if not email:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.RESET_REQUEST_URL)

            OTPCode.objects.filter(email=email).delete()
            otp_code = OTPService.generate_and_save_otp(email)
            EmailService.send_reset_password_email(email, otp_code)

            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.TEMPLATE_NAME)

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)
    
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ChangePasswordView
# Description: Handles password change after OTP verification
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ChangePasswordView(BaseAuthView):
    """
    - Handles password update after OTP verification
    - Validates password inputs
    """
    TEMPLATE_NAME = 'accounts/resetpassword.html'
    OTP_VERIFICATION_URL = 'account:verify-otp'
    RESET_REQUEST_URL = 'account:forgotpassword'

    def get(self, request):
        """Display password change form if session and OTP are valid"""
        return self._render_password_form(request)

    def post(self, request):
        """Handle password update"""
        return self._update_password(request)

    def _render_password_form(self, request):
        try:
            if not self._is_verified_otp(request):
                return redirect(self.OTP_VERIFICATION_URL)
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def _update_password(self, request):
        try:
            if not self._is_verified_otp(request):
                return redirect(self.OTP_VERIFICATION_URL)

            email = request.session.get('email_address')
            new_password = request.POST.get('newpassword', '').strip()
            confirm_password = request.POST.get('confirmpassword', '').strip()

            valid, error_message = FormValidator.validate_password_reset(new_password, confirm_password)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME)

            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            del request.session['email_address']
            messages.success(request, 'Password changed successfully.')
            return redirect(self.login_url)

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return redirect(self.RESET_REQUEST_URL)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

    def _is_verified_otp(self, request):
        """Ensure session email and verified OTP record exist"""
        email = request.session.get('email_address')
        if not email:
            messages.error(request, 'Session expired. Please request a new OTP.')
            return False

        try:
            otp_record = OTPCode.objects.get(email=email)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return False
            return True
        except OTPCode.DoesNotExist:
            messages.error(request, 'OTP verification not found.')
            return False

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: UserSignupView
# Description: Handles user registration
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class UserSignupView(BaseAuthView):
    """
    - Handles user registration
    - Validates form inputs
    - Prevents duplicate registration
    - Generates and sends OTP for email verification
    """
    TEMPLATE_NAME = 'accounts/signup.html'
    OTP_VERIFICATION_URL = 'account:otp_verification'

    def get(self, request):
        """Render signup form"""
        return self._render_signup_form(request)

    def post(self, request):
        """Process signup form submission"""
        return self._process_signup_form(request)

    def _render_signup_form(self, request, form_data=None):
        try:
            return render(request, self.TEMPLATE_NAME, {'form_data': form_data or {}})
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def _process_signup_form(self, request):
        try:
            email = request.POST.get('emailaddress', '').strip().lower()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirmpassword', '').strip()

            form_data = {
                'email': email,
                'username': username,
                'password': password,
            }

            # Validate signup input
            valid, error_message = FormValidator.validate_signup(
                email, username, password, confirm_password
            )

            if not valid:
                messages.error(request, error_message)
                return self._render_signup_form(request, form_data)

            # Check for existing user
            if self._is_existing_email(email):
                return self._handle_existing_email(request, email, form_data)

            # Save form data to session
            request.session['signup_data'] = form_data
            request.session.set_expiry(timedelta(minutes=10))

            # Send OTP
            self._send_otp(email, username)

            messages.success(request, 'A verification code has been sent to your email.')
            return redirect(self.OTP_VERIFICATION_URL)

        except SMTPException:
            messages.error(request, 'We were unable to send the verification email. Please try again later.')
            return redirect(self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.TEMPLATE_NAME)

    def _is_existing_email(self, email):
        return User.objects.filter(email=email).exists()

    def _handle_existing_email(self, request, email, form_data):
        user = User.objects.get(email=email)
        if user.auth_method == 'google':
            messages.error(request, 'This email is associated with a Google account. Please sign in using Google.')
            return redirect(self.login_url)
        messages.error(request, 'This email is already registered. Please use a different email.')
        return self._render_signup_form(request, form_data)

    def _send_otp(self, email, username):
        OTPCode.objects.filter(email=email).delete()
        otp_code = OTPService.generate_and_save_otp(email)
        EmailService.send_verification_email(username, email, otp_code)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: VerifyOTPView
# Description: Handles OTP verification during registration
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class VerifyOTPView(BaseAuthView):
    """
    - Verifies OTP entered by the user during signup
    - Ensures session and OTP validity
    - Redirects user to role selection page upon success
    """
    TEMPLATE_NAME = 'accounts/otp_verification.html'
    SIGNUP_URL = 'account:signup'
    ROLE_SELECTION_URL = 'account:roles'

    def get(self, request):
        """Render OTP verification form"""
        return self._render_otp_form(request)

    def post(self, request):
        """Process submitted OTP"""
        return self._verify_otp(request)

    def _render_otp_form(self, request):
        try:
            if not request.session.get('signup_data'):
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.SIGNUP_URL)
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def _verify_otp(self, request):
        try:
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.SIGNUP_URL)

            email = signup_data.get('email')
            otp_entered = self._get_otp_from_request(request)

            if not otp_entered or len(otp_entered) != 6:
                messages.error(request, 'Please enter a valid 6-digit OTP.')
                return self._render_otp_form(request)

            otp_record = OTPCode.objects.get(email=email)

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return self._render_otp_form(request)

            if otp_entered != str(otp_record.otp_code):
                messages.error(request, 'Invalid OTP. Please try again.')
                return self._render_otp_form(request)

            otp_record.is_verified = True
            otp_record.save()

            messages.success(request, 'OTP verified successfully.')
            return redirect(self.ROLE_SELECTION_URL)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return self._render_otp_form(request)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.SIGNUP_URL)

    def _get_otp_from_request(self, request):
        """Helper method to concatenate 6-digit OTP from form inputs"""
        return ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
       
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: GenerateNewOTPView
# Description: Handles OTP regeneration during registration
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class GenerateNewOTPView(BaseAuthView):
    """
    - Regenerates and sends a new OTP to the user's email during signup
    - Validates session and signup data before sending
    """
    TEMPLATE_NAME = 'accounts/otp_verification.html'
    SIGNUP_URL = 'account:signup'

    def get(self, request):
        """Trigger new OTP generation"""
        return self._generate_and_send_otp(request)

    def _generate_and_send_otp(self, request):
        try:
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.SIGNUP_URL)

            email = signup_data.get('email')
            username = signup_data.get('username')

            OTPCode.objects.filter(email=email).delete()
            otp_code = OTPService.generate_and_save_otp(email)
            EmailService.send_verification_email(username, email, otp_code)

            messages.success(request, 'A new verification code has been sent to your email.')
            return render(request, self.TEMPLATE_NAME)

        except SMTPException:
            messages.error(request, 'We were unable to send the verification email. Please try again later.')
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.SIGNUP_URL)  
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: UserRoleRedirectView
# Description: Handles role selection after registration
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class UserRoleRedirectView(BaseAuthView):
    """
    - Handles role selection after successful OTP verification
    - Creates the user and associated profile (client/freelancer)
    """
    TEMPLATE_NAME = 'accounts/roleselection.html'
    SIGNUP_URL = 'account:signup'
    OTP_VERIFICATION_URL = 'account:otp_verification'
    LOGIN_URL = 'account:login'

    def get(self, request):
        """Display role selection form"""
        return self._render_role_form(request)

    def post(self, request):
        """Process selected role and finalize account creation"""
        return self._create_user_with_role(request)

    def _render_role_form(self, request):
        try:
            if not self._is_otp_verified(request):
                return redirect(self.OTP_VERIFICATION_URL)
            return render(request, self.TEMPLATE_NAME)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def _create_user_with_role(self, request):
        try:
            if not self._is_otp_verified(request):
                return redirect(self.OTP_VERIFICATION_URL)

            signup_data = request.session.get('signup_data')
            role = request.POST.get('role', '').strip().lower()

            if role not in ['client', 'freelancer']:
                messages.error(request, 'Please select a valid role.')
                return render(request, self.TEMPLATE_NAME)

            user = User.objects.create_user(
                email=signup_data['email'],
                username=signup_data['username'],
                password=signup_data['password'],
                role=role,
                is_verified=True,
                auth_method='traditional'
            )

            self._create_profile_for_user(user, role)

            del request.session['signup_data']
            messages.success(request, "You have successfully created an account.")
            return redirect(self.LOGIN_URL)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.SIGNUP_URL)

    def _is_otp_verified(self, request):
        """Check if OTP is verified in session"""
        signup_data = request.session.get('signup_data')
        if not signup_data:
            messages.error(request, 'Session expired. Please sign up again.')
            return False

        try:
            otp_record = OTPCode.objects.get(email=signup_data.get('email'))
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return False
            return True
        except OTPCode.DoesNotExist:
            messages.error(request, 'OTP verification is missing.')
            return False

    def _create_profile_for_user(self, user, role):
        """Create associated client or freelancer profile"""
        profile_map = {
            'client': Client,
            'freelancer': Freelancer
        }
        profile_model = profile_map.get(role)
        if profile_model:
            profile_model.objects.create(user=user)
  
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: UserLogoutView
# Description: Handles user logout
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class UserLogoutView(View):
    """
    - Handles user logout
    - Clears the session and redirects to login with feedback
    """
    LOGIN_URL = 'account:login'

    def get(self, request):
        """Logs out the user and redirects to login page"""
        return self._logout_user(request)

    def _logout_user(self, request):
        try:
            logout(request)
            messages.success(request, 'You have successfully logged out.')
            return redirect(self.LOGIN_URL)
        except Exception as e:
            print(f"[Logout Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.LOGIN_URL)

        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: OAuthRoleSelectionView
# Description: Handles role selection for OAuth users
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------      
class OAuthRoleSelectionView(BaseAuthView):
    """
    - Handles role selection for OAuth-authenticated users (e.g., Google)
    - Creates user, downloads profile picture, links SocialAccount, and redirects to home
    """
    TEMPLATE_NAME = 'accounts/oauth_role_selection.html'

    def get(self, request):
        """Display role selection form for OAuth users"""
        return self._render_role_form(request)

    def post(self, request):
        """Process selected role and complete account creation"""
        return self._process_role_selection(request)

    def _render_role_form(self, request):
        try:
            if not request.session.get('sociallogin'):
                messages.error(request, 'Invalid request.')
                return redirect(self.login_url)

            email = request.session.get('sociallogin_email')
            if not email:
                messages.error(request, 'Email information missing.')
                return redirect(self.login_url)

            return render(request, self.TEMPLATE_NAME, {'email': email})
        except Exception as e:
            print(f"[OAuth GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _process_role_selection(self, request):
        try:
            serialized_sociallogin = request.session.get('sociallogin')
            if not serialized_sociallogin:
                messages.error(request, 'Invalid request.')
                return redirect(self.login_url)

            role = request.POST.get('role', '').strip().lower()
            if role not in ['client', 'freelancer']:
                messages.error(request, 'Please select a valid role.')
                return render(request, self.TEMPLATE_NAME, {
                    'email': request.session.get('sociallogin_email')
                })

            sociallogin = SocialLogin.deserialize(serialized_sociallogin)
            email = sociallogin.account.extra_data.get('email')
            full_name = sociallogin.account.extra_data.get('name', '')
            profile_picture_url = self._get_high_res_picture(sociallogin)

            # Generate unique username
            username = self._generate_unique_username(email)

            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                is_verified=True,
                auth_method='google'
            )
            user.set_password(str(uuid.uuid4()))  # Set random password for OAuth users

            if profile_picture_url:
                self._save_profile_picture(user, username, profile_picture_url)

            user.save()

            # Link social account
            SocialAccount.objects.create(
                user=user,
                provider=sociallogin.account.provider,
                uid=sociallogin.account.uid,
                extra_data=sociallogin.account.extra_data
            )

            # Create role-based profile
            self._create_user_profile(user, role)

            # Log in and cleanup
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            self._clear_oauth_session(request)

            messages.success(request, 'You have successfully logged in.')
            return redirect(self.home_url)

        except Exception as e:
            print(f"[OAuth POST Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _get_high_res_picture(self, sociallogin):
        """Return higher resolution profile picture if available (Google specific)"""
        pic_url = sociallogin.account.extra_data.get('picture')
        if pic_url and 's96-c' in pic_url:
            return pic_url.replace('s96-c', 's256-c')
        return pic_url

    def _generate_unique_username(self, email):
        """Generate a unique username based on email prefix"""
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def _save_profile_picture(self, user, username, url):
        """Download and save profile picture from URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = f"google_profile_{username}.jpg"
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_images'))
                saved_filename = fs.save(filename, ContentFile(response.content))
                user.profile_image = os.path.basename(saved_filename)
        except Exception as e:
            print(f"[Profile Pic Error]: {e}")

    def _create_user_profile(self, user, role):
        """Create corresponding role profile"""
        role_model_map = {
            'client': Client,
            'freelancer': Freelancer
        }
        model = role_model_map.get(role)
        if model:
            model.objects.create(user=user)

    def _clear_oauth_session(self, request):
        """Remove all OAuth-related session keys"""
        for key in ['sociallogin', 'sociallogin_email', 'sociallogin_provider', 'oauth_timestamp']:
            request.session.pop(key, None)
