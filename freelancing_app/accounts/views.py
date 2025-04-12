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
    

class UserLoginView(BaseAuthView):
    """View for user login"""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        """Display login form"""
        try:
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        """Process login form submission"""
        try:
            email = request.POST.get('emailaddress', '').strip().lower()
            password = request.POST.get('password', '').strip()
            login_data = {'email': email} 

            # Form validation
            valid, error_message = FormValidator.validate_login(email, password)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, {'form_data': login_data})
            
            # Check for Google-authenticated user
            google_user = User.objects.filter(email=email, auth_method='google').first()
            if google_user:
                messages.error(request, 'This email is registered with Google. Please login with Google.')
                return render(request, self.template_name, {'form_data': login_data})
            
            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect(self.home_url)
            
            # Handle failed authentication
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Incorrect password. Please try again.')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
                
            return render(request, self.template_name, {'form_data': login_data})
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)
        
        
class ForgotPasswordView(BaseAuthView):
    """Handle password reset request"""
    template_name = 'accounts/reset_password_request.html'
    otp_verification_url = 'account:verify-otp'
    
    def get(self, request):
        """Display password reset form"""
        try:
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def post(self, request):
        """Process password reset request"""
        try:
            email_address = request.POST.get('email').strip().lower()
            if not email_address:
                messages.error(request, 'Please enter your email address.')
                return render(request, self.template_name)
            
            # Get user and handle OTP
            user = User.objects.get(email=email_address)
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = OTPService.generate_and_save_otp(email_address)
            EmailService.send_reset_password_email(email_address, otp_code)
            
            # Set session data
            request.session['email_address'] = email_address
            request.session.set_expiry(timedelta(minutes=10))

            messages.success(request, 'An OTP has been sent to your email address.')
            return redirect(self.otp_verification_url)

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return render(request, self.template_name)

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.template_name)

        except Exception as e:
            print(f"Exception in ForgotPasswordView: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)
        

class PasswordResetOTPVerifyView(BaseAuthView):
    """Handle OTP verification for password reset"""
    template_name = 'accounts/reset_password_otp_verification.html'
    reset_password_request_url = 'account:forgotpassword'
    password_reset_url = 'account:change-password'
    
    def get(self, request):
        """Display OTP verification form"""
        try:
            if not request.session.get('email_address'):
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            return render(request, self.template_name)
        except Exception as e:
            print(f"Exception in PasswordResetOTPVerifyView: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def post(self, request):
        """Verify OTP for password reset"""
        try:
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
        
            # Collect OTP from form
            otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
            if not otp_entered or len(otp_entered) != 6:
                messages.error(request, 'Please enter a valid 6-digit OTP.')
                return render(request, self.template_name)
            
            # Verify OTP
            otp_record = OTPCode.objects.get(email=email_address)
            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP expired. Please request a new one.')
                return render(request, self.template_name)

            if otp_entered == str(otp_record.otp_code):
                otp_record.is_verified = True
                otp_record.save()
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.password_reset_url)

            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.template_name)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.template_name)

        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)
        
        
class ForgotPasswordResendOTPView(BaseAuthView):
    """Handle OTP resend for password reset"""
    template_name = 'accounts/reset_password_otp_verification.html'
    reset_password_request_url = 'account:forgotpassword'
        
    def get(self, request):
        """Resend OTP for password reset"""
        try:
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = OTPService.generate_and_save_otp(email_address)
            EmailService.send_reset_password_email(email_address, otp_code)
            
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.template_name)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.template_name)
        
        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.template_name)

        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)
        

class ChangePasswordView(BaseAuthView):
    """Handle password change after OTP verification"""
    template_name = 'accounts/resetpassword.html'
    otp_verification_url = 'account:verify-otp'
    reset_password_request_url = 'account:forgotpassword'
    
    def get(self, request):
        """Display password change form"""
        try:
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)
            return render(request, self.template_name)
        
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        """Process password change"""
        try:
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)
            
            new_password = request.POST.get('newpassword')
            confirm_password = request.POST.get('confirmpassword')
            valid, error_message = FormValidator.validate_password_reset(new_password, confirm_password)
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name)
            
            # Update user password
            user = User.objects.get(email=email_address)
            user.password = make_password(new_password)
            user.save()
            
            # Clean up session
            del request.session['email_address']
            messages.success(request, 'Password changed successfully.')
            return redirect(self.login_url)

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return redirect(self.reset_password_request_url)
        
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

class UserSignupView(BaseAuthView):
    """Handle user registration"""
    template_name = 'accounts/signup.html'
    otp_verification_url = 'account:otp_verification'
    
    def get(self, request):
        """Display registration form"""
        try:
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        """Process registration form"""
        try:
            email_address = request.POST.get('emailaddress').strip().lower()
            username = request.POST.get('username').strip()
            password = request.POST.get('password').strip()
            confirm_password = request.POST.get('confirmpassword').strip()

            signup_data = {
                'email': email_address,
                'username': username,
                'password': password,
            }

            # Form validation
            valid, error_message = FormValidator.validate_signup(
                email_address, username, password, confirm_password
            )

            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, {'form_data': signup_data})

            # Check existing user
            if User.objects.filter(email=email_address).exists():
                user = User.objects.get(email=email_address)
                if user.auth_method == 'google':
                    messages.error(request, 'This email is registered with Google. Please login with Google.')
                    return redirect(self.login_url)
                else:
                    messages.error(request, 'This email is already registered. Please use a different email.')
                    return render(request, self.template_name, {'form_data': signup_data})

            # Store signup data in session
            request.session['signup_data'] = signup_data
            request.session.set_expiry(timedelta(minutes=10))
            
            # Generate and send OTP
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = OTPService.generate_and_save_otp(email_address)
            EmailService.send_verification_email(username, email_address, otp_code)   
            
            messages.success(request, 'An OTP has been sent to your email address.')
            return redirect(self.otp_verification_url)
                     
        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return redirect(self.template_name)
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.template_name)
        

class VerifyOTPView(BaseAuthView):
    """Handle OTP verification during registration"""
    template_name = 'accounts/otp_verification.html'
    user_role_url = 'account:roles'
    signup_url = 'account:signup'
    
    def get(self, request):
        """Display OTP verification form"""
        try:
            if not request.session.get('signup_data'):
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)  
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def post(self, request):
        """Verify OTP during registration"""
        try:
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            # Collect OTP from form
            otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
            if not otp_entered or len(otp_entered) != 6:
                messages.error(request, 'Please enter a valid 6-digit OTP.')
                return render(request, self.template_name)

            # Verify OTP
            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP has expired. Please regenerate your OTP.')
                return render(request, self.template_name)

            if otp_entered == str(otp_record.otp_code):
                otp_record.is_verified = True
                otp_record.save()
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.user_role_url)
            
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.template_name)
        
        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.template_name)
        
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)
        

class GenerateNewOTPView(BaseAuthView):
    """Handle OTP regeneration during registration"""
    template_name = 'accounts/otp_verification.html'  
    
    def get(self, request):
        """Generate and send new OTP"""
        try:
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url) 
            
            email_address = signup_data.get('email')
            username = signup_data.get('username')
            
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = OTPService.generate_and_save_otp(email_address)
            EmailService.send_verification_email(username, email_address, otp_code)
            
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.template_name)  

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.template_name)
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)   
        

class UserRoleRedirectView(BaseAuthView):
    """Handle role selection after registration"""
    template_name = 'accounts/roleselection.html'  
    otp_verification_url = 'account:otp_verification'
    signup_url = 'account:signup'  

    def get(self, request):
        """Display role selection form"""
        try:
            signup_data = request.session.get('signup_data')  
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)
            
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def post(self, request):
        """Process role selection and create user"""
        try:
            signup_data = request.session.get('signup_data')  
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)

            # Create user
            username = signup_data.get('username')
            password = signup_data.get('password')
            role = request.POST.get('role', '').strip().lower()
            
            if role not in ['client', 'freelancer']:
                messages.error(request, 'Please select a valid role.')
                return render(request, self.template_name)
            
            user = User.objects.create_user(
                email=email_address,
                username=username,
                password=password,
                role=role,
                is_verified=True,
                auth_method='traditional'
            )
            
            # Create corresponding profile
            role_models = {
                "client": Client,
                "freelancer": Freelancer
            }
            role_models[role].objects.create(user=user)
            
            # Clean up session
            del request.session['signup_data']
            messages.success(request, "You have successfully created an account.")
            return redirect(self.login_url)

        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)
        

class UserLogoutView(View):
    """Handle user logout"""
    login_url = 'account:login'
    
    def get(self, request):
        """Log out the user"""
        try:
            logout(request)
            messages.success(request, 'You have successfully logged out.')
            return redirect(self.login_url)
        except Exception as e:
            print(f"Exception in UserLogoutView: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)
        
        
class OAuthRoleSelectionView(BaseAuthView):
    """Handle role selection for OAuth users"""
    template_name = 'accounts/oauth_role_selection.html'
    
    def get(self, request):
        """Display role selection form for OAuth users"""
        try:
            if not request.session.get('sociallogin'):
                messages.error(request, 'Invalid request.')
                return redirect(self.login_url)
            
            email = request.session.get('sociallogin_email')
            if not email:
                messages.error(request, 'Email information missing.')
                return redirect(self.login_url)
            
            return render(request, self.template_name, {'email': email})
        
        except Exception as e:
            print(f"Exception in OAuthRoleSelectionView.get: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)
    
    def post(self, request):
        """Process role selection and create OAuth user"""
        try:
            # Validate request
            serialized_sociallogin = request.session.get('sociallogin')
            if not serialized_sociallogin:
                messages.error(request, 'Invalid request.')
                return redirect(self.login_url)
            
            # Validate role
            role = request.POST.get('role')
            if not role or role not in ['client', 'freelancer']:
                messages.error(request, 'Please select a valid role.')
                return render(request, self.template_name, {
                    'email': request.session.get('sociallogin_email')
                })
            
            # Process social login data
            sociallogin = SocialLogin.deserialize(serialized_sociallogin)
            email = sociallogin.account.extra_data.get('email')
            full_name = sociallogin.account.extra_data.get('name', '')
            
            # Handle profile picture
            profile_picture_url = None
            if sociallogin.account.provider == 'google':
                profile_picture_url = sociallogin.account.extra_data.get('picture')
                if profile_picture_url and 's96-c' in profile_picture_url:
                    profile_picture_url = profile_picture_url.replace('s96-c', 's256-c')
            
            # Create unique username
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                full_name=full_name,
                role=role.lower(),
                is_verified=True,
                auth_method='google'
            )
            
            # Set random password for OAuth user
            user.set_password(str(uuid.uuid4()))
            
            # Download and save profile picture if available
            if profile_picture_url:
                self._save_profile_picture(user, username, profile_picture_url)
            
            user.save()
            
            # Create social account connection
            SocialAccount.objects.create(
                user=user,
                provider=sociallogin.account.provider,
                uid=sociallogin.account.uid,
                extra_data=sociallogin.account.extra_data
            )
            
            # Create profile based on role
            if role == 'client':
                Client.objects.create(user=user)
            elif role == 'freelancer':
                Freelancer.objects.create(user=user)
            
            # Log in the user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Clean up session
            keys_to_remove = ['sociallogin', 'sociallogin_email', 'sociallogin_provider', 'oauth_timestamp']
            for key in keys_to_remove:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'You have successfully logged in.')
            return redirect(self.home_url)
            
        except Exception as e:
            print(f"Exception in OAuthRoleSelectionView.post: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def _save_profile_picture(self, user, username, url):
        """Helper method to save profile picture from URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = f"google_profile_{username}.jpg"
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_images'))
                saved_filename = fs.save(filename, ContentFile(response.content))
                user.profile_image = os.path.basename(saved_filename)
        except Exception as e:
            print(f"Failed to save profile picture: {e}")