from django.views import View
from django.db import DatabaseError
from django.shortcuts import render, redirect, HttpResponse
from django.utils import timezone
from . import utils
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from .models import User, OTPCode, Client, Freelancer
from . import formvalidation

class UserLoginView(View):
    """Class-based view for user login."""
    
    def get(self, request):
        # Render the login page
        return render(request, 'accounts/login.html')

    def post(self, request):
        # Retrieve email and password from the form
        email = request.POST.get(utils.EMAIL_ADDRESS).strip()
        password = request.POST.get(utils.PASSWORD).strip()
        
        if not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/login.html')

        if " " in password:
            messages.error(request, "Password should not contain spaces.")
            return render(request, 'accounts/login.html')
        
        # Check if email exists in the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Email not found
            messages.error(request, "Invalid email address.")
            return render(request, 'accounts/login.html')

        # Check if the entered password matches the stored hashed password
        if user.check_password(password):
            login(request, user)  # Authenticate the user
            # Redirect to the appropriate dashboard
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
        print(email_address)    
        
        if not email_address:
            messages.error(request, "Please enter email address.")
            return render(request, 'accounts/requestotp.html')
        
        user = User.objects.filter(email=email_address)
        
        if user:
            # Store the email in the session
            request.session['email_address'] = email_address

            otp_code = utils.generate_and_save_otp(email_address)
            utils.send_reset_password_email(email_address, otp_code)
            
            return redirect('accounts:resetpassword')
        
        else:
            messages.error(request, "Email not found")
            return render(request, 'accounts/requestotp.html')
            
class PasswordResetView(View):
    """Class-based view for OTP verification during password reset."""
    
    def get(self, request):
        # Render the OTP verification page
        return render(request, 'accounts/passwordresetotp.html')

    def post(self, request):
        # Retrieve the entered OTP
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
        
        if not otp_entered:
            messages.error(request, "Please enter OTP code.")
            return render(request, 'accounts/otpverification.html')
        
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out. Please request OTP again.")
            return redirect('accounts:forgotpassword')  # Assuming the name for the request OTP URL is 'forgot_password'

        try:
            # Fetch the latest OTP record for the email (ordered by generated time)
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return render(request, 'accounts/passwordresetotp.html')
            else:
                if otp_entered == str(otp_record.otp_code):
                    messages.success(request, "OTP verified successfully.")
                    # Redirect to the password reset page
                    return redirect('accounts:changepassword')  # The page where the user can change their password
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
                    return render(request, 'accounts/passwordresetotp.html')

        except OTPCode.DoesNotExist:
            # If no OTP record is found
            messages.error(request, "No OTP record found for this email.")
            return render(request, 'accounts/otpverification.html')

        except DatabaseError as e:
            # Handle any database-related exceptions (like a crash or query failure)
            messages.error(request, "An error occurred while fetching OTP.")
            return redirect('accounts:forgot_password')

        except Exception as e:
            # Catch any other exceptions that might occur
            messages.error(request, "An unexpected error occurred.")
            return redirect('accounts:forgot_password')

class ForgotPasswordResendOTPView(View):
    def get(self, request):
        """Method to resend OTP when the user clicks 'Click to resend'."""
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            # Generate a new OTP
            otp_code = utils.generate_and_save_otp(email_address)  
            utils.send_reset_password_email(email_address, otp_code)

            messages.success(request, "A new OTP has been sent to your email.")
            return render(request, 'accounts/otpverification.html')

        except Exception as e:
            messages.error(request, "An error occurred while resending the OTP.")
            return redirect('accounts:otp_verification')
        
class ChangePasswordView(View):
    
    def get(self, request):
        return render(request, 'accounts/resetpassword.html')
    
    def post(self, request):
        # Get the new password and confirm password from the form
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')

        # Check if the password fields are filled
        if not new_password or not confirm_password:
            messages.error(request, "Please fill in both password fields.")
            return render(request, 'accounts/resetpassword.html')

        # Check if the new password matches the confirm password
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/resetpassword.html')

        # Password validation (optional, you can customize as needed)
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/resetpassword.html')

        # You can add more password validation logic here (e.g., special characters, numbers, etc.)

        # Get the email stored in the session (from the OTP verification flow)
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session expired. Please request the OTP again.")
            return redirect('accounts:forgotpassword')

        try:
            # Fetch the user by email
            user = User.objects.get(email=email_address)

            # Update the user's password
            user.password = make_password(new_password)
            user.save()

            # Clear the session to prevent reuse of old session data
            del request.session['email_address']

            messages.success(request, "Password changed successfully.")
            return redirect('accounts:login')
        
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('accounts:forgotpassword')
        

class UserSignupView(View):
    
    """Class-based view for user signup."""
    template_name = 'accounts/signup.html'

    def get(self, request):
        # Render the signup page
        return render(request, self.template_name)

    def post(self, request):
        # Retrieving inputs from the signup form
        email_address = request.POST.get(utils.EMAIL_ADDRESS).strip()
        username = request.POST.get(utils.USERNAME).strip()
        password = request.POST.get(utils.PASSWORD).strip()
        confirm_password = request.POST.get(utils.CONFIRM_PASSWORD).strip()

        # Hash the password before storing in the session
        hashed_password = make_password(password)

        # Store the form data temporarily in the session
        signup_data = {
            'email': email_address,
            'username': username,
            'password': hashed_password,
        }
        request.session['signup_data'] = signup_data

        # Validate the form
        valid, error_message = formvalidation.validate_signup_form(
            email_address, username, password, confirm_password
        )

        if not valid:
            messages.error(request, error_message)
            return render(request, self.template_name, {'form_data': signup_data})

        # Store the email in the session
        request.session['email_address'] = email_address

        # Generate OTP and send verification email
        otp_code = utils.generate_and_save_otp(email_address)
        utils.send_verification_email(username, email_address, otp_code)

        return redirect('accounts:otp_verification')

class VerifyOTPView(View):
    """Class-based view for OTP verification."""
    
    def get(self, request):
        # Render the OTP verification page
        return render(request, 'accounts/otpverification.html')

    def post(self, request):
        # Retrieve the entered OTP
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
        
        if not otp_entered:
            messages.error(request, "Please enter OTP code.")
            return render(request, 'accounts/otpverification.html')
        
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            # Fetch the latest OTP record for the email (order by generated time)
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return render(request, 'accounts/otpverification.html')
            else:
                if otp_entered == str(otp_record.otp_code):
                    messages.success(request, "OTP verified successfully.")
                    return redirect('accounts:roles')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
                    return render(request, 'accounts/otpverification.html')

        except DatabaseError as e:
            # Handle any database-related exceptions (like a crash or query failure)
            messages.error(request, "An error occurred while fetching OTP.")
            return redirect('accounts:signup')

        except Exception as e:
            # Catch any other exceptions that might occur
            messages.error(request, "An unexpected error occurred.")
            return redirect('accounts:signup')
        
class ResendOTPView(View):
    def get(self, request):
        """Method to resend OTP when the user clicks 'Click to resend'."""
        email_address = request.session.get('email_address')

        signup_data = request.session.get('signup_data')
        username = signup_data['username']

        if not email_address:
            messages.error(request, "Session timed out.")
            return redirect('accounts:signup')

        try:
            # Generate a new OTP
            otp_code = utils.generate_and_save_otp(email_address)  
            utils.send_verification_email(username, email_address, otp_code)

            messages.success(request, "A new OTP has been sent to your email.")
            return render(request, 'accounts/otpverification.html')

        except Exception as e:
            messages.error(request, "An error occurred while resending the OTP.")
            return redirect('accounts:otp_verification')
    
class UserRoleRedirectView(View):
    
    """Class-based view for role selection and user creation."""
    def get(self, request):
        # Render the role selection page
        return render(request, 'accounts/roleselection.html')

    def post(self, request):
        # Retrieve signup data from the session
        signup_data = request.session.get('signup_data')
        if not signup_data:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('accounts:signup')

        email_address = signup_data['email']
        username = signup_data['username']
        hashed_password = signup_data['password']
        role = request.POST.get("role", "").strip()

        # Create a new User object
        user = User.objects.create(
            email=email_address,
            username=username,
            password=hashed_password,
            role=role,
            is_verified=True
        )

        # Create a related Client or Freelancer object
        if role == 'client':
            Client.objects.create(user=user)
        elif role == 'freelancer':
            Freelancer.objects.create(user=user)

        # Clear session data
        del request.session['signup_data']

        messages.success(request, "Account created successfully.")
        return redirect('accounts:login')

