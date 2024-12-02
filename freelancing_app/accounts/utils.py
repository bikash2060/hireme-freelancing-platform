from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTPCode
import random
from datetime import timedelta
from django.utils.timezone import now

# Login/Signup Form Parameters
EMAIL_ADDRESS = "emailaddress"
USERNAME = "username"
PASSWORD = "password"
CONFIRM_PASSWORD = "confirmpassword"

def send_verification_email(username, email_address, otp_code):
    # Prepare HTML email content
    email_html_content = render_to_string('emailtemplate/emailtemplate.html', {
        'username': username,
        'otp': otp_code,
    })

    # Prepare subject and sender details
    subject = "Verify Your Email"
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]

    # Create the email message
    email = EmailMultiAlternatives(subject, f"Your OTP code is {otp_code}", from_email, to_email)
    
    # Attach the HTML alternative content
    email.attach_alternative(email_html_content, "text/html")
    
    # Send the email
    email.send(fail_silently=False)

def send_reset_password_email(email_address, otp_code):
    # Prepare HTML email content
    email_html_content = render_to_string('emailtemplate/passwordrequest.html', {
        'username': email_address,
        'otp': otp_code,
    })

    # Prepare subject and sender details
    subject = "Reset your password"
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]

    # Create the email message
    email = EmailMultiAlternatives(subject, f"Your OTP code is {otp_code}", from_email, to_email)
    
    # Attach the HTML alternative content
    email.attach_alternative(email_html_content, "text/html")
    
    # Send the email
    email.send(fail_silently=False)
    
def generate_and_save_otp(email):
    otp = f"{random.randint(100000, 999999)}"
    OTPCode.objects.create(
        otp_code=otp,
        email=email,
        otp_generated_time=now(),
        otp_expired_time=now() + timedelta(minutes=1)
    )
    return otp