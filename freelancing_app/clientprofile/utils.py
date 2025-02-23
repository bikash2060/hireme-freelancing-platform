import os
import re
from datetime import datetime
from accounts.models import User

def validate_username(username, request=None):
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
    
    try:
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                return False, "Username already taken."
    except Exception as e:
        return False, "Something went wrong. Please try again later."
    return True, ""

def validate_profile_image(profile_image):
    valid_extensions = ['.png', '.jpg', '.jpeg']
    file_extension = os.path.splitext(profile_image.name)[1].lower()
    
    if file_extension not in valid_extensions:
        return False, "Only JPG, PNG, or JPEG file types are allowed."
    
    max_size = 10 * 1024 * 1024  
    if profile_image.size > max_size:
        return False, "File size exceeds the 10MB limit."

    return True, "File is valid."

def validate_personal_info(first_name, middle_name, last_name, phone_number, bio, languages, request=None):
    
    try:
        if not first_name or first_name.lower() == "none":
            return False, "First name is required."
        if len(first_name.split()) > 1:
            return False, "First name cannot contain spaces."
        if len(first_name) < 5 or len(first_name) > 50:
            return False, "First name must be between 5 and 50 characters."

        if middle_name:
            if len(middle_name.split()) > 1:
                return False, "Middle name cannot contain spaces."
            if len(middle_name) < 5 or len(middle_name) > 50:
                return False, "Middle name must be between 5 and 50 characters."

        if not last_name or last_name.lower() == "none":
            return False, "Last name is required."
        if len(last_name.split()) > 1:
            return False, "Last name cannot contain spaces."
        if len(last_name) < 2 or len(last_name) > 50:
            return False, "Last name must be between 2 and 50 characters."

        if not phone_number or phone_number.lower() == "none":
            return False, "Phone number is required."
        if not phone_number.isdigit() or len(phone_number) != 10:
            return False, "Phone number must be exactly 10 digits."
        if not phone_number.startswith(('98', '97', '99')):
            return False, "Phone number must start with a valid prefix (e.g., 98, 97, 99)."

        if phone_number:
            if User.objects.filter(phone_number=phone_number).exclude(id=request.user.id).exists():
                return False, "This phone number is already registered."

        if not languages:
            return False, "At least one language is required."

        if bio and len(bio) > 500:
            return False, "Bio should not exceed 500 characters."

        return True, ""
  
    except Exception as e:
        return False, "Something went wrong. Please try again later."

def create_company(company_logo, company_name, position, start_month, start_year, end_month, end_year, location, currently_working, months):
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
    
    try:
        start_year = int(start_year)
    except ValueError:
        return False, "Invalid start year."
    
    start_month_num = list(months.keys()).index(start_month) + 1  
    start_date = (int(start_year), start_month_num)
    
    current_year = datetime.now().year
    current_month = datetime.now().month

    if start_year > current_year or (start_year == current_year and start_month_num > current_month):
        return False, "Start date cannot be in the future."
    
    if not currently_working:
        if not end_year or not end_month:
            return False, "End date is required if you are not currently working."

        try:
            end_year = int(end_year)
            end_month_num = list(months.keys()).index(end_month) + 1 
        except ValueError:
            return False, "Invalid end year or month."
        
        if end_year > current_year or (end_year == current_year and end_month_num > current_month):
            return False, "End date cannot be in the future."

        if (end_year < start_year) or (end_year == start_year and end_month_num < start_month_num):
            return False, "End date cannot be before start date."
    
    if not location or len(location.strip()) == 0:
        return False, "Location is required."
    
    return True, ""

def validate_password(old_password, new_password, confirm_password, user):
    if not old_password or not new_password or not confirm_password:
        return False, "All fields are required."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    if not user.check_password(old_password):
        return False, "Old Password doesn't match."

    if len(new_password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[A-Z]', new_password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r'[0-9]', new_password):
        return False, "Password must contain at least one number."

    if not re.search(r'[@$!%*?&]', new_password):
        return False, "Password must contain at least one special character."

    return True, ""