import os
import re
from datetime import datetime
from accounts.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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

        if bio and len(bio) > 1000:
            return False, "Bio should not exceed 500 characters."

        return True, ""
  
    except Exception as e:
        return False, "Something went wrong. Please try again later."
    
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

def validate_freelancer_skills_form(experience, hourly_rate, selected_skills):
    if not experience:
        return False, 'Experience is required.'
    
    try:
        experience = float(experience)
    except ValueError:
        return False, 'Invalid experience value.'

    if not hourly_rate:
        return False, 'Hourly rate is required.'
    
    try:
        hourly_rate = float(hourly_rate)
        if hourly_rate < 1:
            return False, 'Hourly rate must be at least 1 NPR.'
    except ValueError:
        return False, 'Invalid hourly rate value.'

    if not selected_skills:
        return False, 'At least one skill must be selected.'

    return True, None  

def validate_education(institution_logo, institution_name, level, start_month, start_year, end_month, end_year, location, currently_studying, months):
    if institution_logo:
        valid_extensions = ['.png', '.jpg', '.jpeg']
        file_extension = os.path.splitext(institution_logo.name)[1].lower()
        
        if file_extension not in valid_extensions:
            return False, "Only JPG, PNG, or JPEG file types are allowed."
        
        max_size = 10 * 1024 * 1024  # 10MB
        if institution_logo.size > max_size:
            return False, "File size exceeds the 10MB limit."

    if not institution_name or len(institution_name.strip()) == 0:
        return False, "Institution name is required."
    
    institution_name = institution_name.strip()
    if len(institution_name) < 3:
        return False, "Institution name should be at least 3 characters long."
    
    if len(institution_name) > 100:
        return False, "Institution name should not exceed 100 characters."

    if not level or len(level.strip()) == 0:
        return False, "Education level is required."

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

    if not currently_studying:
        if not end_year or not end_month:
            return False, "End date is required if you are not currently studying."

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

def validate_certificate(certificate_logo, certificate_name, certificate_provider, issue_month, issue_year, certificate_url, months):

    if certificate_logo:
        valid_extensions = ['.png', '.jpg', '.jpeg']
        file_extension = os.path.splitext(certificate_logo.name)[1].lower()

        if file_extension not in valid_extensions:
            return False, "Only JPG, PNG, or JPEG file types are allowed."

        max_size = 10 * 1024 * 1024  # 10MB
        if certificate_logo.size > max_size:
            return False, "File size exceeds the 10MB limit."

    if not certificate_name:
        return False, "Certificate name is required."
    
    if len(certificate_name) < 4:
        return False, "Certificate name must be at least 5 characters long."
    
    if certificate_name[0].isdigit():
        return False, "Certificate name should not start with a number."
    
    if not certificate_provider:
        return False, "Certificate provider is required."
    
    if len(certificate_provider) < 3:
        return False, "Certificate provider must be at least 5 characters long."
    
    if certificate_provider[0].isdigit():
        return False, "Certificate provider should not start with a number."

    if not issue_month or not issue_year:
        return False, "Issue date is required."

    try:
        issue_year = int(issue_year)
    except ValueError:
        return False, "Invalid issue year."

    if issue_month.lower() not in months:
        return False, "Invalid issue month."

    issue_month_num = list(months.keys()).index(issue_month.lower()) + 1  

    current_year = datetime.now().year
    current_month = datetime.now().month

    if issue_year > current_year or (issue_year == current_year and issue_month_num > current_month):
        return False, "Issue date cannot be in the future."
    
    if certificate_url:
        validate_url = URLValidator()
        try:
            validate_url(certificate_url)
        except ValidationError:
            return False, "Invalid certificate URL format."

    return True, ""