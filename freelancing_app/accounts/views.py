from django.views import View
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from . import utils, formvalidation
from .models import User, OTPCode, Client, Freelancer
from django.utils import timezone


class UserLoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get(utils.EMAIL_ADDRESS).strip()
        password = request.POST.get(utils.PASSWORD).strip()

        if not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/login.html')

        if " " in password:
            messages.error(request, "Password should not contain spaces.")
            return render(request, 'accounts/login.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email address.")
            return render(request, 'accounts/login.html')

        if user.check_password(password):
            login(request, user)
            if user.role == 'client':
                return redirect('clientdashboard:dashboard')
            elif user.role == 'freelancer':
                return redirect('freelancerdashboard:dashboard')
        else:
            messages.error(request, "Incorrect password.")
            return render(request, 'accounts/login.html')


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'accounts/requestotp.html')

    def post(self, request):
        email_address = request.POST.get('email')
        
        if not email_address:
            messages.error(request, "Please enter email address.")
            return render(request, 'accounts/requestotp.html')

        user = User.objects.filter(email=email_address)

        if user:
            request.session['email_address'] = email_address
            otp_code = utils.generate_and_save_otp(email_address)
            utils.send_reset_password_email(email_address, otp_code)
            return redirect('accounts:resetpassword')

        messages.error(request, "Email not found")
        return render(request, 'accounts/requestotp.html')


class PasswordResetView(View):
    def get(self, request):
        return render(request, 'accounts/passwordresetotp.html')

    def post(self, request):
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        if not otp_entered:
            messages.error(request, "Please enter OTP code.")
            return render(request, 'accounts/otpverification.html')

        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out. Please request OTP again.")
            return redirect('accounts:forgotpassword')

        try:
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return render(request, 'accounts/passwordresetotp.html')

            if otp_entered == str(otp_record.otp_code):
                messages.success(request, "OTP verified successfully.")
                return redirect('accounts:changepassword')

            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/passwordresetotp.html')

        except OTPCode.DoesNotExist:
            messages.error(request, "No OTP record found for this email.")
            return render(request, 'accounts/otpverification.html')

        except DatabaseError:
            messages.error(request, "An error occurred while fetching OTP.")
            return redirect('accounts:forgot_password')

        except Exception:
            messages.error(request, "An unexpected error occurred.")
            return redirect('accounts:forgot_password')


class ForgotPasswordResendOTPView(View):
    def get(self, request):
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            otp_code = utils.generate_and_save_otp(email_address)
            utils.send_reset_password_email(email_address, otp_code)
            messages.success(request, "A new OTP has been sent to your email.")
            return render(request, 'accounts/otpverification.html')

        except Exception:
            messages.error(request, "An error occurred while resending the OTP.")
            return redirect('accounts:otp_verification')


class ChangePasswordView(View):
    def get(self, request):
        return render(request, 'accounts/resetpassword.html')

    def post(self, request):
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')

        if not new_password or not confirm_password:
            messages.error(request, "Please fill in both password fields.")
            return render(request, 'accounts/resetpassword.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/resetpassword.html')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/resetpassword.html')

        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session expired. Please request the OTP again.")
            return redirect('accounts:forgotpassword')

        try:
            user = User.objects.get(email=email_address)
            user.password = make_password(new_password)
            user.save()

            del request.session['email_address']
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:login')

        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('accounts:forgotpassword')


class UserSignupView(View):
    template_name = 'accounts/signup.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email_address = request.POST.get(utils.EMAIL_ADDRESS).strip()
        username = request.POST.get(utils.USERNAME).strip()
        password = request.POST.get(utils.PASSWORD).strip()
        confirm_password = request.POST.get(utils.CONFIRM_PASSWORD).strip()

        hashed_password = make_password(password)
        signup_data = {
            'email': email_address,
            'username': username,
            'password': hashed_password,
        }
        request.session['signup_data'] = signup_data

        valid, error_message = formvalidation.validate_signup_form(
            email_address, username, password, confirm_password
        )

        if not valid:
            messages.error(request, error_message)
            return render(request, self.template_name, {'form_data': signup_data})

        request.session['email_address'] = email_address
        otp_code = utils.generate_and_save_otp(email_address)
        utils.send_verification_email(username, email_address, otp_code)

        return redirect('accounts:otp_verification')


class VerifyOTPView(View):
    def get(self, request):
        return render(request, 'accounts/otpverification.html')

    def post(self, request):
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        if not otp_entered:
            messages.error(request, "Please enter OTP code.")
            return render(request, 'accounts/otpverification.html')

        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return render(request, 'accounts/otpverification.html')

            if otp_entered == str(otp_record.otp_code):
                messages.success(request, "OTP verified successfully.")
                return redirect('accounts:roles')

            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/otpverification.html')

        except DatabaseError:
            messages.error(request, "An error occurred while fetching OTP.")
            return redirect('accounts:signup')

        except Exception:
            messages.error(request, "An unexpected error occurred.")
            return redirect('accounts:signup')


class ResendOTPView(View):
    def get(self, request):
        email_address = request.session.get('email_address')
        signup_data = request.session.get('signup_data')
        username = signup_data['username']

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            otp_code = utils.generate_and_save_otp(email_address)
            utils.send_verification_email(username, email_address, otp_code)
            messages.success(request, "A new OTP has been sent to your email.")
            return render(request, 'accounts/otpverification.html')

        except Exception:
            messages.error(request, "An error occurred while resending the OTP.")
            return redirect('accounts:otp_verification')


class UserRoleRedirectView(View):
    def get(self, request):
        return render(request, 'accounts/roleselection.html')

    def post(self, request):
        signup_data = request.session.get('signup_data')

        if not signup_data:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('accounts:signup')

        email_address = signup_data['email']
        username = signup_data['username']
        hashed_password = signup_data['password']
        role = request.POST.get("role", "").strip()

        user = User.objects.create(
            email=email_address,
            username=username,
            password=hashed_password,
            role=role,
            is_verified=True
        )

        if role == "client":
            Client.objects.create(user=user)
            messages.success(request, "You have successfully signed up as a client.")
            return redirect('accounts:login')

        elif role == "freelancer":
            Freelancer.objects.create(user=user)
            messages.success(request, "You have successfully signed up as a freelancer.")
            return redirect('accounts:login')

        messages.error(request, "Invalid role selection.")
        return redirect('accounts:roles')
