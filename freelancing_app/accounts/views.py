from django.shortcuts import render, redirect
from . import utils
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import *
from django.core.mail import send_mail
from freelancing_app.settings import EMAIL_HOST_USER
import random, re
from django.core.exceptions import ObjectDoesNotExist

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
        
        # Check for empty fields
        if not email_address or not username or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('signup')
        
        # Email validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email_address):
            messages.error(request, "Enter a valid email address.")
            return redirect('signup')
        
        # Password and confirm password match validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # Password complexity validation
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('signup')
        
        if not re.search(r'[A-Z]', password):
            messages.error(request, "Password must contain at least one uppercase letter.")
            return redirect('signup')
        
        if not re.search(r'[0-9]', password):
            messages.error(request, "Password must contain at least one number.")
            return redirect('signup')
        
        if not re.search(r'[@$!%*?&]', password):
            messages.error(request, "Password must contain at least one special character.")
            return redirect('signup')

        # Username cannot be only numbers
        if username.isdigit():
            messages.error(request, "Username cannot be only numbers.")
            return redirect('signup')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')
        
        if User.objects.filter(email=email_address).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        # Generate OTP and save in session
        otp = random.randint(100000, 999999)
        request.session['signup_data'] = {'email': email_address, 'username': username, 'password': password}
        request.session['otp'] = otp

        # Send verification email
        send_mail(
            "Verify Your Email",
            f"Your OTP code is {otp}",
            EMAIL_HOST_USER,
            [email_address],
            fail_silently=False,
        )

        return redirect('verifyotp')

    return render(request, 'accounts/signup.html')

def verify_otp(request):
    if request.method == 'POST':
        # Retrieve the entered OTP from the form
        entered_otp = ''.join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])
        
        # Retrieve stored OTP and signup data from session
        stored_otp = request.session.get('otp')
        signup_data = request.session.get('signup_data')  # Contains email, username, and password

        # Validate session data
        if not stored_otp or not signup_data:
            messages.error(request, "Session expired or invalid. Please try again.")
            return redirect('signup')

        # Check if the entered OTP matches the stored OTP
        if entered_otp == str(stored_otp):
            try:
                # Create the user and set as active
                user = User.objects.create_user(
                    username=signup_data['username'],
                    email=signup_data['email'],
                    password=signup_data['password']
                )
                user.is_active = True
                user.save()

                # Clear session data
                request.session.pop('otp', None)

                return redirect('user-redirect')  

            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
                return redirect('signup')
        
        # If OTP does not match
        messages.error(request, "Invalid OTP. Please try again.")
        return render(request, 'accounts/email_verification.html')

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
