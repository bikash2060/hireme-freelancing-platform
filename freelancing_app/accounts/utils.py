from django.contrib.auth.backends import ModelBackend
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTPCode
from .models import User
import random

class EmailService:
    """Service class for handling email-related operations"""
    
    @staticmethod
    def send_verification_email(username: str, email_address: str, otp_code: str) -> None:
        """
        Send email verification with OTP code for signup
        
        Args:
            username: Recipient's username
            email_address: Recipient's email address
            otp_code: Generated OTP code
        """
        template_name = "emailtemplate/signup_verification_email.html"
        subject = "Verify Your Email"
        
        EmailService._send_email(
            template_name=template_name,
            subject=subject,
            recipient_email=email_address,
            context={
                'username': username,
                'otp': otp_code,
            },
            plain_text=f"Your OTP code is {otp_code}"
        )

    @staticmethod
    def send_reset_password_email(email_address: str, otp_code: str) -> None:
        """
        Send password reset email with OTP code
        
        Args:
            email_address: Recipient's email address
            otp_code: Generated OTP code
        """
        template_name = "emailtemplate/passwordrequest.html"
        subject = "Reset your password"
        
        EmailService._send_email(
            template_name=template_name,
            subject=subject,
            recipient_email=email_address,
            context={
                'username': email_address,
                'otp': otp_code,
            },
            plain_text=f"Your OTP code is {otp_code}"
        )

    @staticmethod
    def _send_email(
        template_name: str,
        subject: str,
        recipient_email: str,
        context: dict,
        plain_text: str
    ) -> None:
        """
        Internal method to send email with HTML and plain text alternatives
        
        Args:
            template_name: Path to HTML template
            subject: Email subject
            recipient_email: Recipient's email address
            context: Context data for template rendering
            plain_text: Fallback plain text content
        """
        email_html_content = render_to_string(template_name, context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email]
        )
        email.attach_alternative(email_html_content, "text/html")
        email.send(fail_silently=False)


class OTPService:
    """Service class for handling OTP-related operations"""
    
    @staticmethod
    def generate_and_save_otp(email: str) -> str:
        """
        Generate a 6-digit OTP and save it to database
        
        Args:
            email: Email address to associate with the OTP
            
        Returns:
            Generated OTP code
        """
        otp = f"{random.randint(100000, 999999)}"
        OTPCode.objects.create(
            otp_code=otp,
            email=email,
        )
        return otp


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with their email address
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user based on email and password
        
        Args:
            request: HttpRequest object
            email: User's email address
            password: User's password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            # Logging would be better than print statements in production
            print(f"Password mismatch for user: {email}")
        except User.DoesNotExist:
            print(f"Authentication attempt for non-existent user: {email}")
        return None