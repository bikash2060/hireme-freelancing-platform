from django.views import View
from smtplib import SMTPException
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from .utils import *
from .formvalidation import *
from .models import *
from django.utils import timezone
from datetime import timedelta

class UserLoginView(View):
    login_template = 'accounts/login.html'
    login_url = 'account:login'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            return render(request, self.login_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)  
        
            email = request.POST.get('emailaddress', '').strip().lower()
            password = request.POST.get('password', '').strip()
            login_data = {'email': email} 

            valid, error_message = validate_login_form(email, password)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.login_template, {'form_data': login_data})
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect(self.home_url)
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Incorrect password. Please try again.')
                return render(request, self.login_template, {'form_data': login_data})
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
                return render(request, self.login_template, {'form_data': login_data})
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)
        
class ForgotPasswordView(View):    
    reset_password_request_template = 'accounts/reset_password_request.html'
    otp_verification_url = 'account:verify-otp'
    login_url = 'account:login'
    home_url = 'home:home'

    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
            return render(request, self.reset_password_request_template)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)

            email_address = request.POST.get('email').strip().lower()
            if not email_address:
                messages.error(request, 'Please enter your email address.')
                return render(request, self.reset_password_request_template)
            
            user = User.objects.get(email=email_address)
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = generate_and_save_otp(email_address)
            send_reset_password_email(email_address, otp_code)
            
            request.session['email_address'] = email_address
            request.session.set_expiry(timedelta(minutes=10))

            messages.success(request, 'An OTP has been sent to your email address.')
            return redirect(self.otp_verification_url)

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return render(request, self.reset_password_request_template)

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.reset_password_request_template)

        except Exception as e:
            print("Exception inside ForgotPasswordView: ", e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

class PasswordResetOTPVerifyView(View):
    otp_verification_template = 'accounts/reset_password_otp_verification.html'
    reset_password_request_url = 'account:forgotpassword'
    password_reset_url = 'account:change-password'
    login_url = 'account:login'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)

            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            return render(request, self.otp_verification_template)
        
        except Exception as e:
            print("Exception inside PasswordResetOTPVerifyView: ", e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.login_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
        
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
        
            otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
            if not otp_entered:
                messages.error(request, 'Please enter the OTP.')
                return render(request, self.otp_verification_template)
        
            if len(otp_entered) != 6:
                messages.error(request, 'OTP must be 6 digits.')
                return render(request, self.otp_verification_template)
            
            otp_record = OTPCode.objects.get(email=email_address)
            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP expired. Please request a new one.')
                return render(request, self.otp_verification_template)

            if otp_entered == str(otp_record.otp_code):
                otp_record.is_verified = True
                otp_record.save()
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.password_reset_url)

            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.otp_verification_template)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.otp_verification_template)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

class ForgotPasswordResendOTPView(View):
    otp_verification_template = 'accounts/reset_password_otp_verification.html'
    password_reset_url = 'account:change-password'
    reset_password_request_url = 'account:forgotpassword'
    login_url = 'account:login'
        
    def get(self, request):
        try:
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = generate_and_save_otp(email_address)
            send_reset_password_email(email_address, otp_code)
            
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.otp_verification_template)

        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.otp_verification_template)
        
        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.otp_verification_template)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

class ChangePasswordView(View):
    reset_password_template = 'accounts/resetpassword.html'
    otp_verification_url = 'account:verify-otp'
    reset_password_request_url = 'account:forgotpassword'
    login_url = 'account:login'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
            email_address = request.session.get('email_address')
            if not email_address:
                messages.error(request, 'Session expired. Please request a new OTP.')
                return redirect(self.reset_password_request_url)
            
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)
            return render(request, self.reset_password_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
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
            valid, error_message = validate_reset_password_form(new_password, confirm_password)
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.reset_password_template)
            
            user = User.objects.get(email=email_address)
            user.password = make_password(new_password)
            user.save()
            
            del request.session['email_address']
            messages.success(request, 'Password changed successfully.')
            return redirect(self.login_url)

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return redirect(self.reset_password_request_url)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.login_url)

class UserSignupView(View):
    signup_template = 'accounts/signup.html'
    otp_verification_url = 'account:otp_verification'
    home_url = 'home:home'
    signup_url = 'account:signup'   

    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            return render(request, self.signup_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
            email_address = request.POST.get('emailaddress').strip().lower()
            username = request.POST.get('username').strip()
            password = request.POST.get('password').strip()
            confirm_password = request.POST.get('confirmpassword').strip()

            signup_data = {
                'email': email_address,
                'username': username,
                'password': password,
            }

            valid, error_message = validate_signup_form(
                email_address, username, password, confirm_password
            )

            if not valid:
                messages.error(request, error_message)
                return render(request, self.signup_template, {'form_data': signup_data})

            request.session['signup_data'] = signup_data
            request.session.set_expiry(timedelta(minutes=10))
            
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = generate_and_save_otp(email_address)
            send_verification_email(username, email_address, otp_code)   
            
            messages.success(request, 'An OTP has been sent to your email address.')
            return redirect(self.otp_verification_url)
                     
        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return redirect(self.signup_url)
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.signup_url)

class VerifyOTPView(View):
    otp_verification_template = 'accounts/otp_verification.html'
    user_role_url = 'account:roles'
    signup_url = 'account:signup'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)  
            
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)  
            return render(request, self.otp_verification_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
            if not otp_entered:
                messages.error(request, 'Please enter the OTP.')
                return render(request, self.otp_verification_template)
            
            if len(otp_entered) != 6:
                messages.error(request, 'OTP must be 6 digits.')
                return render(request, self.otp_verification_template)

            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP has expired. Please regenerate your OTP.')
                return render(request, self.otp_verification_template)

            if otp_entered == str(otp_record.otp_code):
                otp_record.is_verified = True
                otp_record.save()
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.user_role_url)
            
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.otp_verification_template)
        
        except OTPCode.DoesNotExist:
            messages.error(request, 'No OTP found for this email.')
            return render(request, self.otp_verification_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)

class GenerateNewOTPView(View):
    otp_verification_template = 'accounts/otp_verification.html'  
    signup_url = 'account:signup'  
    
    def get(self, request):
        try:
            signup_data = request.session.get('signup_data')
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url) 
            
            email_address = signup_data.get('email')
            username = signup_data.get('username')
            
            OTPCode.objects.filter(email=email_address).delete()
            otp_code = generate_and_save_otp(email_address)
            send_verification_email(username, email_address, otp_code)
            
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.otp_verification_template)  

        except SMTPException:
            messages.error(request, 'Unable to send email. Please try again later.')
            return render(request, self.otp_verification_template)
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)  

class UserRoleRedirectView(View):
    user_role_template = 'accounts/roleselection.html'  
    otp_verification_url = 'account:otp_verification'
    login_url = 'account:login'  
    signup_url = 'account:signup'  
    home_url = 'home:home'

    def get(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
            
            signup_data = request.session.get('signup_data')  
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)
            
            return render(request, self.user_role_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                return redirect(self.home_url)
                    
            signup_data = request.session.get('signup_data')  
            if not signup_data:
                messages.error(request, 'Session expired. Please sign up again.')
                return redirect(self.signup_url)
            
            email_address = signup_data.get('email')
            otp_record = OTPCode.objects.get(email=email_address)
            if not otp_record.is_verified:
                messages.error(request, 'Please verify your OTP first.')
                return redirect(self.otp_verification_url)

            email_address = signup_data.get('email')
            username = signup_data.get('username')
            password = signup_data.get('password')
            
            role = request.POST.get('role', '').strip()
            
            user = User.objects.create_user(
                email=email_address,
                username=username,
                password=password,
                role=role.lower(),  
                is_verified=True
            )
            
            role_models = {
                "client": Client,
                "freelancer": Freelancer
            }
            
            role_models[role].objects.create(user=user)
            messages.success(request, "You have successfully created an account.")
            
            del request.session['signup_data']
            return redirect(self.login_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.signup_url)

class UserLogoutView(View):
    login_url = 'account:login'
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect(self.login_url)