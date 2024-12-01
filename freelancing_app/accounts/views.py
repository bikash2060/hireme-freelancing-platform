from django.shortcuts import render, redirect
from django.utils import timezone
from . import utils
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from . import formvalidation
from django.contrib.auth.hashers import make_password

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

        # Check if the entered password matches the stored hashed password
        if user.check_password(password):  # Compare raw password with the hashed password
            # Authenticate the user using the email and password
            login(request, user)
            # Redirect the user to the appropriate dashboard based on their role
            if user.role == 'client':
                return redirect('client_dashboard')  # Replace with actual URL for client dashboard
            elif user.role == 'freelancer':
                return redirect('freelancer_dashboard')  # Replace with actual URL for freelancer dashboard
        else:
            # If password does not match, display an error message
            messages.error(request, "Incorrect password.")
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
        
        # Hash the password before storing in the session
        hashed_password = make_password(password)
        
        # Store the form data entered by the user temporarily in the session
        signup_data = {
            'email': email_address,
            'username': username,
            'password': hashed_password
        }
        request.session['signup_data'] = signup_data
        
        # Validate form using the validate_signup_form function
        valid, error_message = formvalidation.validate_signup_form(email_address, username, password, confirm_password)

        if not valid:
            # If validation fails, show the error and return the form with user input
            messages.error(request, error_message)
            return render(request, 'accounts/signup.html', {'form_data': signup_data})
        
        # Store the email in the session
        request.session['email_address'] = email_address
        
        # Generate OTP and save in database
        otp_code = utils.generate_and_save_otp(email_address)
        utils.send_verification_email(username, email_address, otp_code)

        return redirect('accounts:otp_verification')

    return render(request, 'accounts/signup.html')

def verify_otp(request):
    if request.method == 'POST':
        # Retrieve the entered OTP from the form (assuming it's entered in 6 fields)
        otp_entered = ''.join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])

        # Retrieve the email from the session
        email_address = request.session.get('email_address')

        if not email_address:
            messages.error(request, "Session timed out")
            return redirect('accounts:signup')  # Redirect to the signup page if no email in session

        try:
            # Fetch the latest OTP record for the email (order by generated time)
            otp_record = OTPCode.objects.filter(email=email_address).order_by('-otp_generated_time').first()

            if not otp_record:
                # No OTP found for this email
                messages.error(request, "No OTP found. Please request a new OTP.")
                return redirect('accounts:signup')

            # Check if the OTP has expired
            if otp_record.otp_expired_time < timezone.now():
                # OTP has expired
                messages.error(request, "OTP has expired. Please regenerate your OTP.")
                return redirect('accounts:otp_verification')  

            # If OTP is not expired, check if the entered OTP matches
            if otp_entered == str(otp_record.otp_code):
                # OTP is correct and still valid, proceed with the verification
                messages.success(request, "OTP verified successfully.")
                return redirect('accounts:roles')  
            else:
                # OTP is incorrect
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'accounts/otpverification.html')

        except OTPCode.DoesNotExist:
            # OTP does not match or is not found
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/otpverification.html')

    return render(request, 'accounts/otpverification.html')

def user_redirect(request):
    if request.method == "POST":
        signup_data = request.session.get('signup_data')
        if not signup_data:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('accounts:signup')  

        # Retrieve the data from session
        email_address = signup_data['email']
        username = signup_data['username']
        hashed_password = signup_data['password']  
        
        role = request.POST.get("role", "").strip()
        
        # Create a new User object and save it to the database with the hashed password
        user = User.objects.create(
            email=email_address,
            username=username,
            password=hashed_password,  
            role=role,
            is_verified=True
        )
        
        # Optionally, you can add more fields or actions depending on the role
        if role == 'client':
            Client.objects.create(user=user)  # Assuming you have a Client model
        elif role == 'freelancer':
            Freelancer.objects.create(user=user)  # Assuming you have a Freelancer model

        # Clear session data after account creation
        del request.session['signup_data']

        messages.success(request, "Account created successfully.")
        return redirect('accounts:login')  # Redirect to login page

    return render(request, 'accounts/roleselection.html')
