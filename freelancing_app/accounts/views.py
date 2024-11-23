from django.shortcuts import render, redirect
from . import utils
from django.contrib import messages
import re
from .models import *
from django.core.mail import send_mail
from freelancing_app.settings import EMAIL_HOST_USER
import random

def user_login(request):
    return render(request, 'accounts/login.html')

def user_signup(request):
    if request.method == "POST":
        email_address = request.POST.get(utils.EMAIL_ADDRESS)  
        username = request.POST.get(utils.USERNAME)
        password = request.POST.get(utils.PASSWORD)
        confirm_password = request.POST.get(utils.CONFIRM_PASSWORD)
        
        if not email_address or not username or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('signup')
        
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email_address):
            messages.error(request, "Enter a valid email address.")
            return redirect('signup')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # if User.objects.filter(username=username).exists:
        #     print("This line is being generated.")
        #     messages.error(request, "Username is already taken.")
        #     return redirect('signup')
        
        # if User.objects.filter(email=email_address).exists:
        #     messages.error(request, "An account with this email already exists.")
        #     return redirect('signup')
        
        user = User.objects.create_user(username=username, email=email_address, password=password)
        user.is_active = False
        user.save()
        otp = random.randint(100000,999999)
        request.session['user_email'] = email_address
        request.session['otp'] = otp
        send_mail(
            "Subject here",
            f"Verify your Mail by the OTP: {otp}",
            EMAIL_HOST_USER,
            [email_address],  
            fail_silently=False,
        )
        
        return render(request, 'accounts/email_verification.html')
        
        
    return render(request, 'accounts/signup.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = ''.join([request.POST.get(f'otp{i}') for i in range(1, 7)])

        stored_otp = request.session.get('otp')

        email_address = request.session.get('user_email')

        if entered_otp == str(stored_otp):
            try:
                user = User.objects.get(email=email_address)
                user.is_active = True
                user.is_verified = True  
                user.save()

                del request.session['otp']
                del request.session['user_email']

                return render(request, 'accounts/successpage.html')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return render(request, 'accounts/email_verification.html')

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/email_verification.html')

    return render(request, 'accounts/email_verification.html')

    