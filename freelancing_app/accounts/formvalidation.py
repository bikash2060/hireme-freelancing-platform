import re
from .models import User

def validate_signup_form(email, username, password, confirm_password):

    # Check for empty fields
    if not email or not username or not password or not confirm_password:
        return False, "All fields are required."

    # Email validation
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return False, "Enter a valid email address."
    
    # Password and confirm password match validation
    if password != confirm_password:
        return False, "Passwords do not match."
    
    # Password complexity validation
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."

    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character."
    
    # Username cannot be only numbers
    if username.isdigit():
        return False, "Username cannot be only numbers."
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return False, "Username is already taken."
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return False, "An account with this email already exists."

    # If everything is fine, return True
    return True, ""
