from django.shortcuts import render, redirect
from . import utils
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import *
from django.core.mail import send_mail
from freelancing_app.settings import EMAIL_HOST_USER
import random, re
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from . import formvalidation

def user_login(request):
    if request.method == "POST":
        
        # Retrieve email and password from the form
        email = request.POST.get(utils.EMAIL_ADDRESS)
        password = request.POST.get(utils.PASSWORD)

        # Check if email exists in the database
        try:
            user = User.objects.get(email=email)  # Look up user by email
        except User.DoesNotExist:
            
            # If email is not found, display an error message
            messages.error(request, "Invalid email address.")
            return render(request, 'accounts/login.html')

        # Authenticate the user using username (since Django authentication requires it)
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to the dashboard or any desired page
        else:
            # If authentication fails, show an error message
            messages.error(request, "Incorrect password. Please try again.")
            return render(request, 'accounts/login.html')

    # Render the login page if the request method is not POST
    return render(request, 'accounts/login.html')

def user_signup(request):
    if request.method == "POST":
        
        # Retrieving inputs from signup form
        email_address = request.POST.get(utils.EMAIL_ADDRESS)  
        username = request.POST.get(utils.USERNAME)
        password = request.POST.get(utils.PASSWORD)
        confirm_password = request.POST.get(utils.CONFIRM_PASSWORD)
        
        user_input = {
            'email': email_address, 
            'username': username
        }
        
        # Validate form using the validate_signup_form function
        valid, error_message = formvalidation.validate_signup_form(email_address, username, password, confirm_password)

        if not valid:
            # If validation fails, show the error and return the form with user input
            messages.error(request, error_message)
            user_input = {
                'email': email_address, 
                'username': username
            }
            return render(request, 'accounts/signup.html', {'form_data': user_input})
        
        # Generate OTP and save in session
        otp_code = random.randint(100000, 999999)
        request.session['signup_data'] = {'email': email_address, 'username': username, 'password': password}
        request.session['otp'] = otp_code

        utils.send_verification_email(username, email_address, otp_code)

        return redirect('accounts:otp_verification')

    return render(request, 'accounts/signup.html')

def verify_otp(request):
    if request.method == 'POST':
        # Retrieve the entered OTP from the form
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
        
        # Retrieve stored OTP and signup data from session
        otp_code = request.session.get('otp')
        signup_data = request.session.get('signup_data')  # Contains email, username, and password

        # Verify the OTP
        if otp_entered == str(otp_code):
            # OTP is correct, proceed with the next step (e.g., activate the account)
            messages.success(request, "OTP verified successfully.")
            return redirect('accounts:signup_success')  # Redirect to success page
        else:
            # OTP is incorrect, show an error message
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/otpverification.html')

    return render(request, 'accounts/otpverification.html')

def user_redirect(request):
    if request.method == "POST":
        signup_data = request.session.get('signup_data')
        email_address = signup_data['email']
        
        if not email_address:
            messages.error(request, "Session expired. Please log in again.")
            return redirect('login')  
        
        try:
            user = User.objects.get(email=email_address)
        except ObjectDoesNotExist:
            messages.error(request, "User not found.")
            return redirect('signup')  
        
        role = request.POST.get("role", "").strip()
        
        if role not in ["client", "freelancer"]:
            messages.error(request, "Invalid role selected.")
            return redirect('some_page')  
        
        user.role = role
        user.save()
        
        return redirect('dashboard')  
    
    return render(request, 'accounts/successpage.html')
