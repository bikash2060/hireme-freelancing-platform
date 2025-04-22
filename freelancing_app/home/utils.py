from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
from typing import Union

class ContactEmailService:
    """Service class for handling contact form email operations"""
    
    @staticmethod
    def send_user_confirmation_email(name: str, email_address: str, subject_type: str, message: str) -> None:
        """
        Send confirmation email to user after contact form submission
        
        Args:
            name: User's name
            email_address: User's email address
            subject_type: Type of inquiry
            message: User's message
        """
        template_name = "emailtemplate/contact_confirmation_email.html"
        subject = "We've Received Your Message"
        
        ContactEmailService._send_email(
            template_name=template_name,
            subject=subject,
            recipient_email=email_address,
            context={
                'name': name,
                'subject_type': subject_type,
                'message': message,
                'company_name': 'HireMe',
                'company_email': settings.CONTACT_EMAIL,
                'company_phone': settings.CONTACT_PHONE,
            },
            plain_text=f"Dear {name}, thank you for contacting us. We've received your message regarding '{subject_type}' and will respond shortly."
        )

    @staticmethod
    def send_admin_notification_email(name: str, email_address: str, phone: str, subject_type: str, message: str) -> None:
        """
        Send notification email to admin about new contact form submission
        
        Args:
            name: User's name
            email_address: User's email address
            phone: User's phone number
            subject_type: Type of inquiry
            message: User's message
        """
        template_name = "emailtemplate/contact_admin_notification.html"
        subject = f"New Contact Form Submission: {subject_type}"
        
        admin_emails = [settings.ADMIN_EMAIL]
        
        ContactEmailService._send_email(
            template_name=template_name,
            subject=subject,
            recipient_email=admin_emails,
            context={
                'name': name,
                'email': email_address,
                'phone': phone,
                'subject_type': subject_type,
                'message': message,
                'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            plain_text=f"New contact form submission from {name} ({email_address}). Subject: {subject_type}. Message: {message}"
        )

    @staticmethod
    def _send_email(
        template_name: str,
        subject: str,
        recipient_email: Union[str, list],
        context: dict,
        plain_text: str
    ) -> None:
        """
        Internal method to send email with HTML and plain text alternatives
        
        Args:
            template_name: Path to HTML template
            subject: Email subject
            recipient_email: Recipient's email address(es)
            context: Context data for template rendering
            plain_text: Fallback plain text content
        """
        email_html_content = render_to_string(template_name, context)
        
        recipients = [recipient_email] if isinstance(recipient_email, str) else recipient_email
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients
        )
        email.attach_alternative(email_html_content, "text/html")
        email.send(fail_silently=False)