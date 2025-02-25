import re
from .models import User

def validate_signup_form(email, username, password, confirm_password):
    reserved_words = {
        "admin", "administrator", "root", "superuser", "sysadmin", "moderator", "mod",
        "support", "helpdesk", "service", "client", "freelancer", "user", "guest",
        "owner", "manager", "staff", "team", "developer", "dev", "test", "tester",
        "system", "operator", "security", "bot", "automated", "anonymous", "null",
        "banned", "blocked", "unknown", "default", "account", "password", "database",
        "server", "host", "network", "api", "master", "backup", "debug", "trial",
        "free", "premium", "vip", "official", "mod", "admin1", "admin2"
    }

    try:
        if not email or not username or not password or not confirm_password:
            return False, "All fields are required."

        if " " in email:
            return False, "Email should not contain spaces."
        
        if " " in password or " " in confirm_password:
            return False, "Password should not contain spaces."

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return False, "Enter a valid email address."

        if " " in username:
            return False, "Username should not contain spaces."
        
        if username.isdigit():
            return False, "Username cannot be only numbers."
        
        if username[0].isdigit():
            return False, "Username cannot start with a number."
        
        if len(username) < 5:
            return False, "Username must be at least 5 characters long."
        
        if len(username) > 15:
            return False, "Username must not exceed 15 characters."
        
        if username.lower() in reserved_words:
            return False, "This username is reserved. Please choose another."

        if password != confirm_password:
            return False, "Passwords do not match."

        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number."
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain at least one special character."
        
        if User.objects.filter(username=username).exists():
            return False, "Username is already taken."
        
        if User.objects.filter(email=email).exists():
            return False, "An account with this email already exists."
        
        return True, None
    
    except Exception as e:
        return False, "Something went wrong. Please try again later"

def validate_login_form(email, password):
    
    if not email or not password:
        return False, 'All fields are required.'
    
    if ' ' in password:
        return False, 'Password should not contain spaces.'
    
    return True, None

def validate_reset_password_form(password, confirm_password):
    
    if not password or not confirm_password:
        return False, 'All fields are required.'
    
    if ' ' in password or ' ' in confirm_password:
        return False, 'Password should not contain spaces.'
    
    if password != confirm_password:
        return False, 'Password do not match.'
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character."
    
    return True, None