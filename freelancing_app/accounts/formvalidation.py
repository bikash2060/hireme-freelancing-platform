from django.conf import settings
from .models import User
import re

class FormValidator:
    """
    Utility class for validating user registration, login, and password reset forms.
    Provides consistent validation rules and error messages across the application.
    """
    
    EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    MIN_USERNAME_LENGTH = 5
    MAX_USERNAME_LENGTH = 15
    MIN_PASSWORD_LENGTH = 8

    @classmethod
    def validate_signup(cls, email: str, username: str, password: str, confirm_password: str) -> tuple:
        """
        Validate user registration form data.
        
        Args:
            email: User's email address
            username: Desired username
            password: User's password
            confirm_password: Password confirmation
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        try:
            # Field presence validation
            if not all([email, username, password, confirm_password]):
                return False, "Please complete all required fields."

            # Email validation
            if " " in email:
                return False, "Email address should not contain spaces."
            if not re.match(cls.EMAIL_REGEX, email):
                return False, "Please enter a valid email address."

            # Username validation
            if " " in username:
                return False, "Username cannot contain spaces."
            if username.isdigit():
                return False, "Username must include letters and cannot be purely numeric."
            if username[0].isdigit():
                return False, "Username cannot begin with a number."
            if not cls.MIN_USERNAME_LENGTH <= len(username) <= cls.MAX_USERNAME_LENGTH:
                return False, f"Username must be between {cls.MIN_USERNAME_LENGTH} and {cls.MAX_USERNAME_LENGTH} characters."
            if username.lower() in settings.RESERVED_USERNAMES:
                return False, "This username is not available. Please choose another one."
            if User.objects.filter(username__iexact=username).exists():
                return False, "This username is already in use. Please try a different one."

            # Password validation
            if " " in password or " " in confirm_password:
                return False, "Passwords must not contain spaces."
            if password != confirm_password:
                return False, "Passwords do not match. Please re-enter them."
            
            password_errors = cls._validate_password_strength(password)
            if password_errors:
                return False, password_errors

            return True, None

        except Exception as e:
            # Log the actual error in production
            return False, "An unexpected error occurred. Please try again later."

    @classmethod
    def validate_login(cls, email: str, password: str) -> tuple:
        """
        Validate user login form data.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not email or not password:
            return False, 'Please provide both email and password.'
        return True, None

    @classmethod
    def validate_password_reset(cls, password: str, confirm_password: str) -> tuple:
        """
        Validate password reset form data.
        
        Args:
            password: New password
            confirm_password: Password confirmation
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not password or not confirm_password:
            return False, 'Both password fields are required.'
        if ' ' in password or ' ' in confirm_password:
            return False, 'Passwords must not contain spaces.'
        if password != confirm_password:
            return False, 'Passwords do not match. Please confirm correctly.'
            
        password_errors = cls._validate_password_strength(password)
        if password_errors:
            return False, password_errors
            
        return True, None

    @classmethod
    def _validate_password_strength(cls, password: str) -> str:
        """
        Internal method to validate password strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Error message if validation fails, otherwise empty string
        """
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long."
        if not re.search(r'[A-Z]', password):
            return "Password must include at least one uppercase letter."
        if not re.search(r'[0-9]', password):
            return "Password must include at least one number."
        if not re.search(r'[@$!%*?&]', password):
            return "Password must include at least one special character (@$!%*?&)."
        return ""