from django.views import View
from django.db import DatabaseError
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, login
from django.contrib.auth.hashers import make_password
from . import utils, formvalidation
from .models import User, OTPCode, Client, Freelancer
from django.utils import timezone

#Testing in progress
class UserLoginView(View):
    
    # Template used for rendering the login page
    rendered_template = 'accounts/login.html'
    
    def get(self, request):
        # Renders the login page when the user visits the login URL
        return render(request, self.rendered_template)

    def post(self, request):
        # Retrieves email and password from the POST request
        email = request.POST.get('emailaddress').strip()
        password = request.POST.get('password').strip()
        
        # Validate the login form (check if email and password are valid)
        valid, error_message = formvalidation.validate_login_form(email, password)
        
        if not valid:
            # If validation fails, display an error message and re-render the login page
            messages.error(request, error_message)
            return render(request, self.rendered_template)

        # Use the authenticate method to check user credentials
        user = authenticate(request, email=email, password=password)
        
        print(f"User: {user}")
        
        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            
            # Redirect based on user role
            if user.role == 'client':
                return HttpResponse('Client Dashboard')
            else:
                return HttpResponse('Freelancer Dashboard')
        else:
            # If authentication fails, display an error message and re-render the login page
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request, self.rendered_template)


class ForgotPasswordView(View):
    
    rendered_template = 'accounts/reset_password_request.html'
    
    success_redirect_URL = 'accounts:verify-otp'
    
    def get(self, request):
        return render(request, self.rendered_template)

    def post(self, request):
        email_address = request.POST.get('email')
        
        if not email_address:
            messages.error(request, "Please enter email address.")
            return render(request, self.rendered_template)

        user = User.objects.filter(email=email_address)

        if user:
            request.session['email_address'] = email_address
            otp_code = utils.generate_and_save_otp(email_address)
            utils.send_reset_password_email(email_address, otp_code)
            return redirect(self.success_redirect_URL)

        messages.error(request, "Email not found")
        return render(request, self.rendered_template)


class PasswordResetView(View):
    
    renderd_template = 'accounts/reset_password_otp_verification.html'
    
    success_redirect_URL = 'accounts:change-password'
    
    error_redirect_URL = 'accounts:login'
    
    def get(self, request):
        return render(request, self.renderd_template)

    def post(self, request):
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        if not otp_entered:
            messages.error(request, "Please enter OTP code.")
            return render(request, self.renderd_template)

        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out. Please request OTP again.")
            return redirect(self.error_redirect_URL)

        try:
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return render(request, self.renderd_template)

            if otp_entered == str(otp_record.otp_code):
                messages.success(request, "OTP verified successfully.")
                return redirect(self.success_redirect_URL)

            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, self.renderd_template)

        except OTPCode.DoesNotExist:
            messages.error(request, "No OTP record found for this email.")
            return render(request, 'accounts/otpverification.html')

        except DatabaseError:
            messages.error(request, "An error occurred while fetching OTP.")
            return redirect(self.error_redirect_URL)

        except Exception:
            messages.error(request, "An unexpected error occurred.")
            return redirect(self.error_redirect_URL)


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

#Testing Completed
class UserSignupView(View):
    # Define the template to be rendered for the signup page.
    rendered_template = 'accounts/signup.html'
    
    # URL to redirect upon successful registration
    successful_redirect_URL = 'accounts:otp_verification'

    def get(self, request):
        # Handle GET request to render the signup page.
        # This will display the form for the user to fill out for creating new account.
        return render(request, self.rendered_template)

    def post(self, request):
        """
        Handle POST request when the user submits the signup form.
        1. Retrieve and sanitize the user inputs (email, username, password, and confirm password).
        2. Hash the password before storing it in the session.
        3. Store the sanitized signup data in the session to persist it temporarily.
        4. Validate the form data using the form validation function.
        5. If validation fails, return an error message and re-render the signup page with the existing form data.
        6. If validation passes, store the email in the session and generate an OTP.
        7. Send the OTP to the user's email address for verification.
        8. Redirect the user to the OTP verification page for further steps.
        """
        
        email_address = request.POST.get('emailaddress').strip()
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirmpassword').strip()

        # Hash the password before storing in the session or database later
        hashed_password = make_password(password)

        # Store the form data temporarily in the session to preserve the user's input
        # And avoid re-entering the same values in the form if validation fails.
        signup_data = {
            'email': email_address,
            'username': username,
            'password': hashed_password,
        }

        # Validate the form
        valid, error_message = formvalidation.validate_signup_form(
            email_address, username, password, confirm_password
        )

        if not valid:
            # If validation fails, return an error message and re-render the signup page with the form data
            messages.error(request, error_message)
            return render(request, self.rendered_template, {'form_data': signup_data})

        # If validation passes, store the data in the session
        request.session['signup_data'] = signup_data

        # Generate OTP and send verification email
        otp_code = utils.generate_and_save_otp(email_address)
        utils.send_verification_email(username, email_address, otp_code)

        # Redirect the user to the OTP verification page
        return redirect(self.successful_redirect_URL)

#Testing Completed
class VerifyOTPView(View):
    # Template for rendering the OTP verification form
    rendered_template = 'accounts/otp_verification.html'
    
    # URL to redirect upon successful OTP verification
    successful_redirect_URL = 'accounts:roles'
    
    # URL to redirect if an error occurs during verification
    error_redirect_URL = 'accounts:signup'
    
    def get(self, request):
        """
        Handles GET requests to display the OTP verification form. 
        """
        return render(request, self.rendered_template)

    def post(self, request):
        """
        Handles POST requests to validate the OTP entered by the user.
        - Extracts OTP from the form input.
        - Validates session data for signup details.
        - Verifies the OTP against the database record.
        - Redirects to the appropriate URL based on the validation outcome.
        """
        
        # Extract OTP entered by the user (6 individual fields combined)
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        # Check if OTP is entered
        if not otp_entered:
            messages.error(request, 'Please enter OTP code.')
            return render(request, self.rendered_template)

        # Retrieve signup data from the session
        signup_data = request.session.get('signup_data')

        # Check if signup data exists in the session
        if not signup_data:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect(self.error_redirect_URL)
        
        # Extract email address from signup data
        email_address = signup_data.get('email')

        try:
            # Fetch the latest OTP record for the given email
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()
            
            if not otp_record:
                # Handle case where no OTP record exists for the email
                messages.error(request, 'No OTP record found.')
                return redirect(self.error_redirect_URL)

            # Check if the OTP has expired
            if otp_record.otp_expired_time < timezone.now():
                messages.error(request, 'OTP has expired. Please regenerate your OTP.')
                return render(request, self.rendered_template)

            # Compare the entered OTP with the stored OTP
            if otp_entered == str(otp_record.otp_code):
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.successful_redirect_URL)
            
            # Handle incorrect OTP
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.rendered_template)

        except DatabaseError:
            # Handle database-related errors
            messages.error(request, 'An error occurred while fetching OTP.')
            return redirect(self.error_redirect_URL)

        except Exception:
            messages.error(request, 'An unexpected error occurred.')
            return redirect(self.error_redirect_URL)

#Testing Completed
class GenerateNewOTPView(View):
    
    # Template for OTP verification page
    rendered_template = 'accounts/otp_verification.html'  
    
    # Set the URL to redirect in case of session expiration
    error_redirect_URL = 'accounts:signup'  
    
    def get(self, request):
        
        # Retrieve signup data from the session
        signup_data = request.session.get('signup_data')

        # Check if signup data exists in the session (session should not be expired)
        if not signup_data:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect(self.error_redirect_URL)  # Redirect to signup page if session expired
        
        # Extract email and username from the session data
        email_address = signup_data.get('email')
        username = signup_data.get('username')

        try:
            # Generate and save the new OTP for the user
            otp_code = utils.generate_and_save_otp(email_address)
            
            # Send the OTP to the user's email for verification
            utils.send_verification_email(username, email_address, otp_code)
            
            # Inform the user that a new OTP has been sent successfully
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.rendered_template)  # Render OTP verification page

        except Exception:
            # Handle any unexpected errors during OTP generation or sending email
            messages.error(request, 'An error occurred while resending the OTP.')
            return render(request, self.rendered_template)  

#Testing Completed
class UserRoleRedirectView(View):
    
    # Template for role selection view
    rendered_template = 'accounts/roleselection.html'  
    
    # URL to redirect upon successful signup
    successful_redirect_URL = 'accounts:login'  
    
    # URL to redirect if session expired or other errors
    error_redirect_URL = 'accounts:signup'  

    def get(self, request):
        # Renders the role selection page (GET request)
        return render(request, self.rendered_template)

    def post(self, request):
        # Handles the form submission for selecting user role (POST request)
        
        # Retrieve signup data from session
        signup_data = request.session.get('signup_data')  

        if not signup_data:
            # If signup data is missing or session expired, redirect to signup page
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect(self.error_redirect_URL)

        # Extract user details (email, username, password) from the session
        email_address = signup_data.get('email')
        username = signup_data.get('username')
        hashed_password = signup_data.get('password')
        
        # Get the selected role from the form (client or freelancer)
        role = request.POST.get('role', '').strip()

        # Create a new User instance and save it to the database
        user = User.objects.create_user(
            email=email_address,
            username=username,
            password=hashed_password,
            role=role,
            is_verified=True  
        )

        # Convert role to lowercase for comparison
        role = role.lower() 
                
        # Depending on the role selected, create a corresponding user profile (Client or Freelancer)
        if role == 'client':
            # Create and save the Client profile
            Client.objects.create(user=user)  
            messages.success(request, 'You have successfully signed up as a client.')
            # Redirect to login page after successful signup
            return redirect(self.successful_redirect_URL)  

        elif role == 'freelancer':
            # Create and save the Freelancer profile
            Freelancer.objects.create(user=user)  
            messages.success(request, 'You have successfully signed up as a freelancer.')
            # Redirect to login page after successful signup
            return redirect(self.successful_redirect_URL)  

        # If an invalid role is selected, display an error and redirect to role selection page
        messages.error(request, "Invalid role selection.")
        return redirect('accounts:roles')  # Redirect to role selection page if role is invalid
