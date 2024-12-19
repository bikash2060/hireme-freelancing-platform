from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.backends import ModelBackend
from .models import User
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTPCode
import random
from datetime import timedelta
from django.utils.timezone import now

def send_verification_email(username, email_address, otp_code):
    # Sends an email with an OTP code to the specified user email for verification.
    # Includes both plain text and HTML content to ensure proper display in various email clients.

    # Prepare HTML email content
    email_html_content = render_to_string('emailtemplate/signup_verification_email.html', {
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
    """
    Generates a 6-digit OTP, saves it to the database with an expiration time, and returns the OTP.
    Associates the OTP with the provided email address and ensures it expires in 1 minute.
    """
    otp = f"{random.randint(100000, 999999)}"
    OTPCode.objects.create(
        otp_code=otp,
        email=email,
        otp_generated_time=now(),
        otp_expired_time=now() + timedelta(minutes=2)
    )
    return otp

class EmailBackend(ModelBackend):
    """
    Custom backend for authenticating users using their email and password.
    Inherits from Django's ModelBackend and overrides the authenticate method.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Attempt to retrieve the user by email
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user # Return the authenticated user
            else:
                print("Password mismatch!")  
        except User.DoesNotExist:
            print("User does not exist")  
        return None

