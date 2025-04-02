from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.backends import ModelBackend
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTPCode
from .models import User
import random

def send_verification_email(username, email_address, otp_code):
    signup_verification_email_template = "emailtemplate/signup_verification_email.html"
    email_html_content = render_to_string(signup_verification_email_template, {
        'username': username,
        'otp': otp_code,
    })

    subject = "Verify Your Email"
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]

    email = EmailMultiAlternatives(subject, f"Your OTP code is {otp_code}", from_email, to_email)
    email.attach_alternative(email_html_content, "text/html")
    
    email.send(fail_silently=False)

def send_reset_password_email(email_address, otp_code):
    password_reset_email_template = "emailtemplate/passwordrequest.html"
    email_html_content = render_to_string(password_reset_email_template, {
        'username': email_address,
        'otp': otp_code,
    })

    subject = "Reset your password"
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]

    email = EmailMultiAlternatives(subject, f"Your OTP code is {otp_code}", from_email, to_email)
    email.attach_alternative(email_html_content, "text/html")
    
    email.send(fail_silently=False)
    
def generate_and_save_otp(email):
    otp = f"{random.randint(100000, 999999)}"
    OTPCode.objects.create(
        otp_code=otp,
        email=email,
    )
    return otp

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user 
            else:
                print("Password mismatch!")  
        except User.DoesNotExist:
            print("User does not exist")  
        return None

