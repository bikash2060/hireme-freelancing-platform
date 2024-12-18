from django.views import View
from smtplib import SMTPException
from django.db import DatabaseError
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from . import utils, formvalidation
from .models import User, OTPCode, Client, Freelancer
from django.utils import timezone

# Testing Completed
class UserLoginView(View):
    # Template used for rendering the login page
    rendered_template = 'accounts/login.html'
    
    # URL to redirect upon successful login
    successful_redirect_URL = ''
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('homes:home')
        
        # Renders the login page when the user visits the login URL
        return render(request, self.rendered_template)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('homes:home')
        # Retrieves email and password from the POST request
        email = request.POST.get('emailaddress').strip().lower()
        password = request.POST.get('password').strip()
        
        # Store the form data temporarily in the session to preserve the user's input
        # And avoid re-entering the same values in the form if validation fails.
        login_data = {
            'email': email
        }
        
        # Validate the login form (check if email and password are valid)
        valid, error_message = formvalidation.validate_login_form(email, password)
        
        if not valid:
            # If validation fails, display an error message and re-render the login page
            messages.error(request, error_message)
            return render(request, self.rendered_template, {'form_data': login_data})

        # Use the authenticate method to check user credentials
        try:
            user = authenticate(request, email=email, password=password)
        except Exception as e:
            # Catch any unexpected errors during authentication
            messages.error(request, 'An error occurred while authenticating your credentials. Please try again.')
            return render(request, self.rendered_template, {'form_data': login_data})
        
        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            
            # Set session expiry to 30 minutes
            request.session.set_expiry(30 * 60)
                        
            # Redirect based on user role
            if user.role == 'client':
                return HttpResponse('Client Dashboard')
            else:
                return HttpResponse('Freelancer Dashboard')
        else:
            # If authentication fails, check if the email exists in the database
            try:
                existing_user = User.objects.get(email=email)
                # If the user exists but password doesn't match, display a specific message
                messages.error(request, "Password doesn't match. Please try again.")
                return render(request, self.rendered_template, {'form_data': login_data})
            except User.DoesNotExist:
                # If the user does not exist, display a general invalid credentials message
                messages.error(request, 'Invalid credentials. Please try again.')
                return render(request, self.rendered_template, {'form_data': login_data})

# Testing Completed
class ForgotPasswordView(View):
    # Template used for rendering the password reset request page
    rendered_template = 'accounts/reset_password_request.html'
    
    # URL to redirect to upon successful OTP request
    success_redirect_URL = 'account:verify-otp'
    
    # URL to redirect to in case of an error (e.g., invalid email or unexpected error)
    error_redirect_URL = 'account:login'
    
    def get(self, request):
        # Renders the password reset request page when the user visits the reset password URL
        return render(request, self.rendered_template)

    def post(self, request):
        # Retrieves the email address from the POST request
        email_address = request.POST.get('email')
        
        # Check if the email field is empty
        if not email_address:
            # If no email is provided, display an error message
            messages.error(request, 'Please enter email address.')
            return render(request, self.rendered_template)

        try:
            # Retrieve the user object associated with the provided email
            user = User.objects.get(email=email_address)

            # Check if the user exists in the database
            if not user:
                # If user is not found, display an error message
                messages.error(request, 'Email not found. Please enter correct email.')
                return render(request, self.rendered_template)

            # Delete any existing OTP records for the email address
            OTPCode.objects.filter(email=email_address).delete()

            # Generate and save a new OTP for the provided email address
            otp_code = utils.generate_and_save_otp(email_address)

            try:
                # Attempt to send the OTP to the user's email address
                utils.send_reset_password_email(email_address, otp_code)
            except SMTPException as e:
                # If there is an error sending the email, display a server error message
                messages.error(request, 'Failed to send verification email due to a server issue.')
                return render(request, self.rendered_template)

            # Store the email address in the session to persist it across views
            request.session['email_address'] = email_address
            # Set the session expiration to 5 minutes (300 seconds)
            request.session.set_expiry(300)
            # Redirect the user to the OTP verification page
            return redirect(self.success_redirect_URL)

        except DatabaseError as e:
            # If there is a database error while checking the email address, display a generic error message
            messages.error(request, 'An error occurred while checking the email address. Please try again.')
            return redirect(self.error_redirect_URL)
        
        except Exception as e:
            # Catch any other unexpected errors and display a generic error message
            messages.error(request, 'An unexpected error occurred. Please try again later.')
            return redirect(self.error_redirect_URL)

# Testing Completed
class PasswordResetOTPVerifyView(View):
    
    # Template used for rendering the OTP verification page
    rendered_template = 'accounts/reset_password_otp_verification.html'
    
    # URL to redirect to upon successful OTP verification
    success_redirect_URL = 'account:change-password'
    
    # URL to redirect to in case of an error (e.g., invalid OTP or session expiry)
    error_redirect_URL = 'account:login'
    
    def get(self, request):
        # Renders the OTP verification page when the user visits the OTP verification URL
        return render(request, self.rendered_template)

    def post(self, request):
        # Retrieves the email address stored in the session
        email_address = request.session.get('email_address')

        # Check if the session has expired (i.e., email_address is not in the session)
        if not email_address:
            # If session expired, display an error message and redirect to the forgot password page
            messages.error(request, "Session expired. Please request the OTP again.")
            return redirect('account:forgotpassword')
        
        # Retrieve the OTP entered by the user, formed by concatenating each digit field
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        # Check if the OTP was entered
        if not otp_entered:
            # If OTP is not entered, display an error message
            messages.error(request, 'Please enter OTP code.')
            return render(request, self.rendered_template)
        
        # Ensure the OTP is exactly 6 digits long
        if len(otp_entered) != 6:
            # If OTP length is not 6 digits, display an error message
            messages.error(request, 'OTP must be exactly 6 digits.')
            return render(request, self.rendered_template)

        try:
            # Retrieve the OTP record from the database for the given email
            otp_record = OTPCode.objects.get(email=email_address)

            # Check if the OTP has expired
            if otp_record.otp_expired_time < timezone.now():
                # If OTP is expired, display an error message and prompt for regeneration
                messages.error(request, 'OTP has expired. Please regenerate your OTP.')
                return render(request, self.rendered_template)

            # Compare the entered OTP with the stored OTP
            if otp_entered == str(otp_record.otp_code):
                # If the OTP matches, display success message and redirect to the change password page
                messages.success(request, 'OTP verified successfully.')
                return redirect(self.success_redirect_URL)

            # If the OTP does not match, display an error message
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.rendered_template)

        except OTPCode.DoesNotExist:
            # If no OTP record is found for the email, display an error message
            messages.error(request, 'No OTP record found for this email.')
            return render(request, self.rendered_template)

        except DatabaseError:
            # If there is a database error while fetching the OTP, display an error message
            messages.error(request, 'An error occurred while fetching OTP.')
            return redirect(self.error_redirect_URL)

        except Exception:
            # Catch any other unexpected errors and display a generic error message
            messages.error(request, 'An unexpected error occurred.')
            return redirect(self.error_redirect_URL)

# Testing Completed
class ForgotPasswordResendOTPView(View):
    
    # Template used for rendering the OTP verification page
    rendered_template = 'accounts/reset_password_otp_verification.html'
    
    # URL to redirect to upon successful OTP resend
    success_redirect_URL = 'account:change-password'
    
    # URL to redirect to in case of an error (e.g., session expired or OTP issue)
    error_redirect_URL = 'account:login'
    
    def get(self, request):
        # Retrieves the email address stored in the session
        email_address = request.session.get('email_address')

        # Check if the session has expired (i.e., email_address is not in the session)
        if not email_address:
            # If session expired, display an error message and redirect to the forgot password page
            messages.error(request, "Session expired. Please request the OTP again.")
            return redirect('account:forgotpassword')

        try:
            # Deletes any existing OTP record for the given email
            OTPCode.objects.filter(email=email_address).delete()

            # Generate a new OTP and save it to the database
            otp_code = utils.generate_and_save_otp(email_address)

            # Send the OTP via email
            utils.send_reset_password_email(email_address, otp_code)

            # Display success message and render the OTP verification page
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.rendered_template)

        except OTPCode.DoesNotExist:
            # If no OTP record is found for the email, display an error message
            messages.error(request, 'No OTP record found for this email address.')
            return redirect(self.error_redirect_URL)

        except DatabaseError:
            # If there is a database error while processing the request, display an error message
            messages.error(request, 'An error occurred while processing your request.')
            return redirect(self.error_redirect_URL)

        except Exception as e:
            # Catch any other unexpected errors and display a generic error message
            messages.error(request, 'An unexpected error occurred.')
            return redirect(self.error_redirect_URL)

# Testing Completed
class ChangePasswordView(View):
    # Template used for rendering the change password page
    rendered_template = 'accounts/resetpassword.html'
    
    # URL to redirect to upon successful password change
    success_redirect_URL = 'account:login'
    
    # URL to redirect to in case of error (e.g., session expired or other issues)
    error_redirect_URL = 'account:forgotpassword'
    
    def get(self, request):
        # Renders the change password page when the user accesses the URL
        return render(request, self.rendered_template)

    def post(self, request):
        # Retrieves the email address stored in the session
        email_address = request.session.get('email_address')

        # Check if the session has expired (i.e., email_address is not in the session)
        if not email_address:
            # If session expired, display an error message and redirect to forgot password page
            messages.error(request, "Session expired. Please request the OTP again.")
            return redirect(self.error_redirect_URL)
        
        # Retrieves the new password and the confirmation password from the POST request
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')

        # Validate the new password and confirmation password (check for match and strength)
        valid, error_message = formvalidation.validate_reset_password_form(new_password, confirm_password)
        
        if not valid:
            # If validation fails, display an error message and re-render the change password page
            messages.error(request, error_message)
            return render(request, self.rendered_template)

        try:
            # Attempt to find the user by email address
            user = User.objects.get(email=email_address)
            # Update the user's password and save the changes
            user.password = make_password(new_password)
            user.save()

            # Remove the email address from the session after the password change
            del request.session['email_address']

            # Display a success message and redirect to the login page
            messages.success(request, 'Password changed successfully.')
            return redirect(self.success_redirect_URL)

        except User.DoesNotExist:
            # If the user is not found in the database, display an error message and redirect
            messages.error(request, 'User not found.')
            return redirect(self.error_redirect_URL)
        
        except Exception as e:
            # Catch any other unexpected errors and display a generic error message
            messages.error(request, 'An unexpected error occurred.')
            return redirect(self.error_redirect_URL)

# Testing Completed:
class UserSignupView(View):
    
    # Define the template to be rendered for the signup page.
    rendered_template = 'accounts/signup.html'
    
    # URL to redirect upon successful registration
    successful_redirect_URL = 'account:otp_verification'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('homes:home')
        
        # Handle GET request to render the signup page.
        # This will display the form for the user to fill out for creating new account.
        return render(request, self.rendered_template)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('homes:home')
        
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

        email_address = request.POST.get('emailaddress').strip().lower()
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirmpassword').strip()

        # Store the form data temporarily in the session to preserve the user's input
        # And avoid re-entering the same values in the form if validation fails.
        signup_data = {
            'email': email_address,
            'username': username,
            'password': password,
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
        request.session.set_expiry(300)
        
        # Generate OTP and send verification email
        try:
            # Delete any previous OTP code for the given email address
            OTPCode.objects.filter(email=email_address).delete()
            
            # Generate OTP
            otp_code = utils.generate_and_save_otp(email_address)

            # Send the OTP email
            try:
                utils.send_verification_email(username, email_address, otp_code)
            except SMTPException as e:
                # Handle email-related errors
                messages.error(request, "Failed to send verification email due to a server issue.")
                return render(request, self.rendered_template, {'form_data': signup_data})

        except Exception as e:
            # Handle any unexpected errors during OTP generation or other issues
            messages.error(request, "An error occurred during the signup process.")
            return render(request, self.rendered_template, {'form_data': signup_data})

        # Redirect the user to the OTP verification page
        return redirect(self.successful_redirect_URL)

# Testing Completed
class VerifyOTPView(View):
    # Template for rendering the OTP verification form
    rendered_template = 'accounts/otp_verification.html'
    
    # URL to redirect upon successful OTP verification
    successful_redirect_URL = 'account:roles'
    
    # URL to redirect if an error occurs during verification
    error_redirect_URL = 'account:signup'
    
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
        
        # Check if OTP is exactly 6 digits
        if len(otp_entered) != 6:
            messages.error(request, 'OTP must be exactly 6 digits.')
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
            otp_record = OTPCode.objects.filter(email=email_address).get()
            
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

        except Exception as e:
            messages.error(request, 'An unexpected error occurred.')
            return redirect(self.error_redirect_URL)

# Testing Completed
class GenerateNewOTPView(View):
    
    # Template for OTP verification page
    rendered_template = 'accounts/otp_verification.html'  
    
    # Set the URL to redirect in case of session expiration
    error_redirect_URL = 'account:signup'  
    
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
            # Delete any previous OTP code for the given email address
            OTPCode.objects.filter(email=email_address).delete()
            
            # Generate and save the new OTP for the user
            otp_code = utils.generate_and_save_otp(email_address)
            
            # Send the OTP to the user's email for verification
            try:
                utils.send_verification_email(username, email_address, otp_code)
            except Exception as e:
                messages.error(request, "Failed to send verification email. Please try again.")
                return render(request, self.rendered_template, {'form_data': signup_data})
        
            # Inform the user that a new OTP has been sent successfully
            messages.success(request, 'A new OTP has been sent to your email.')
            return render(request, self.rendered_template)  # Render OTP verification page

        except Exception:
            # Handle any unexpected errors during OTP generation or sending email
            messages.error(request, 'An error occurred while resending the OTP.')
            return render(request, self.rendered_template)  

# Testing Completed
class UserRoleRedirectView(View):
    
    # Template for role selection view
    rendered_template = 'accounts/roleselection.html'  
    
    # URL to redirect upon successful signup
    successful_redirect_URL = 'account:login'  
    
    # URL to redirect if session expired or other errors
    error_redirect_URL = 'account:signup'  

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
        password = signup_data.get('password')
        
        # Get the selected role from the form (client or freelancer)
        role = request.POST.get('role', '').strip()

        # Create a new User instance and save it to the database
        try:
            user = User.objects.create_user(
                email=email_address,
                username=username,
                password=password,
                role=role,
                is_verified=True  
            )
        except Exception as e:
            messages.error(request, 'An error occurred while creating your account.')
            return redirect(self.error_redirect_URL)
        
        # Convert role to lowercase for comparison
        role = role.lower() 
                
        try:
            # Depending on the role selected, create a corresponding user profile (Client or Freelancer)
            if role == 'client':
                # Create and save the Client profile
                Client.objects.create(user=user)
                messages.success(request, 'You have successfully signed up as a client.')
                # Delete the specific session data after successful signup
                del request.session['signup_data']
                return redirect(self.successful_redirect_URL)  # Redirect to login page after successful signup

            else:
                # Create and save the Freelancer profile
                Freelancer.objects.create(user=user)
                messages.success(request, 'You have successfully signed up as a freelancer.')
                # Delete the specific session data after successful signup
                del request.session['signup_data']
                return redirect(self.successful_redirect_URL)  # Redirect to login page after successful signup

        except Exception as e:
            messages.error(request, 'An error occurred while creating your profile.')
            return redirect(self.error_redirect_URL)

class UserLogOutView(View):
    def get(self, request):
        logout(request)
        return redirect('homes:home')

