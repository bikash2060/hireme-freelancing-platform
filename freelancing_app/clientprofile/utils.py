import os
import re
from datetime import datetime

def validate_username(username):
    reserved_words = {
        "admin", "administrator", "root", "superuser", "sysadmin", "moderator", "mod",
        "support", "helpdesk", "service", "client", "freelancer", "user", "guest",
        "owner", "manager", "staff", "team", "developer", "dev", "test", "tester",
        "system", "operator", "security", "bot", "automated", "anonymous", "null",
        "banned", "blocked", "unknown", "default", "account", "password", "database",
        "server", "host", "network", "api", "master", "backup", "debug", "trial",
        "free", "premium", "vip", "official", "mod", "admin1", "admin2"
    }
    
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
    
    return True, ""

def validate_profile_image(profile_image):
    
    valid_extensions = ['.png', '.jpg', '.jpeg']
    file_extension = os.path.splitext(profile_image.name)[1].lower()
    
    if file_extension not in valid_extensions:
        return False, "Only JPG, PNG, or JPEG file types are allowed."
    
    max_size = 10 * 1024 * 1024  # 10 MB
    if profile_image.size > max_size:
        return False, "File size exceeds the 10MB limit."

    return True, "File is valid."

def validate_personal_info(first_name, middle_name, last_name, phone_number, bio, languages):
    
    # First Name Validation
    if not first_name or first_name.lower() == "none":
        return False, "First name is required."
    if len(first_name.split()) > 1:
        return False, "First name cannot contain spaces."
    if len(first_name) < 5 or len(first_name) > 50:
        return False, "First name must be between 5 and 50 characters."
    
    # Middle Name Validation
    if middle_name:
        if len(middle_name.split()) > 1:
            return False, "Middle name cannot contain spaces."
        if len(middle_name) < 5 or len(middle_name) > 50:
            return False, "Middle name must be between 5 and 50 characters."
    
    # Last Name Validation
    if not last_name or last_name.lower() == "none":
        return False, "Last name is required."
    if len(last_name.split()) > 1:
        return False, "Last name cannot contain spaces."
    if len(last_name) < 2 or len(last_name) > 50:
        return False, "Last name must be between 2 and 50 characters."
    
    # Phone Number Validation
    if not phone_number or phone_number.lower() == "none":
        return False, "Phone number is required."
    if not phone_number.isdigit() or len(phone_number) != 10:
        return False, "Phone number must be exactly 10 digits."
    if not phone_number.startswith(('98', '97', '99')):
        return False, "Phone number must start with a valid prefix (e.g., 98, 97, 99)."
    
    # Languages Validation
    if not languages:
        return False, "At least one language is required."
    
    if bio and len(bio) > 500:
        return False, "Bio should not exceed 500 characters."
    
    return True, ""

def create_company(company_logo, company_name, position, start_month, start_year, end_month, end_year, location, url, currently_working, months):
    if company_logo:
        valid_extensions = ['.png', '.jpg', '.jpeg']
        file_extension = os.path.splitext(company_logo.name)[1].lower()
        
        if file_extension not in valid_extensions:
            return False, "Only JPG, PNG, or JPEG file types are allowed."
        
        max_size = 10 * 1024 * 1024  # 10MB
        if company_logo.size > max_size:
            return False, "File size exceeds the 10MB limit."
    
    if not company_name or len(company_name.strip()) == 0:
        return False, "Company name is required."
    
    if not position or len(position.strip()) == 0:
        return False, "Position is required."
    
    if not start_month or not start_year:
        return False, "Start date is required."
    
    start_month_num = list(months.keys()).index(start_month) + 1  
    start_date = (int(start_year), start_month_num)
    
    if not currently_working and (not end_month or not end_year):
        return False, "End date is required if not currently working."
    
    if end_month and end_year:
        end_month_num = list(months.keys()).index(end_month) + 1  
        end_date = (int(end_year), end_month_num)
        
        if end_date < start_date:
            return False, "End date cannot be earlier than start date."
    
    if url and not url.startswith(("http://", "https://")):
        return False, "Invalid URL. Ensure the URL starts with http:// or https://."
    
    return True, ""

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character."
    
    return True, ""