from django.conf import settings
from accounts.models import User
from datetime import datetime
import os
import re

def validate_user_data(profile_image, full_name, username, phone_number, bio, city_id, country_id, request=None):
    try:
        if profile_image:
            valid_extensions = ['.png', '.jpg', '.jpeg']
            file_extension = os.path.splitext(profile_image.name)[1].lower()
            
            if file_extension not in valid_extensions:
                return False, "Only JPG, PNG, or JPEG file types are allowed."
            
            max_size = 10 * 1024 * 1024
            if profile_image.size > max_size:
                return False, "File size exceeds the 10MB limit."

            try:
                from PIL import Image
                Image.open(profile_image).verify()
            except:
                return False, "Invalid image file."

        if not full_name or str(full_name).strip().lower() == "none":
            return False, "Full name is required."
        
        full_name = str(full_name).strip()
        if len(full_name) < 3:
            return False, "Full name must be at least 3 characters long."    
        
        if len(full_name) > 30: 
            return False, "Full name must not exceed 20 characters."
        
        if full_name.isdigit():
            return False, "Full name cannot be only numbers."
        
        if full_name[0].isdigit():
            return False, "Full name cannot start with a number."
        
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', full_name):
            return False, "Full name contains invalid characters."

        if not username:
            return False, "Username is required."
        
        username = str(username).strip()
        if " " in username:
            return False, "Username cannot contain spaces."

        if username.isdigit():
            return False, "Username cannot be only numbers."
        
        if username[0].isdigit():
            return False, "Username cannot start with a number."
        
        if len(username) < 5:
            return False, "Username must be at least 5 characters long."
        
        if len(username) > 30:
            return False, "Username must not exceed 15 characters."
        
        if not re.match(r'^[a-zA-Z0-9_\.]+$', username):
            return False, "Username can only contain letters, numbers, underscores."
        
        if username.lower() in settings.RESERVED_USERNAMES:
            return False, "This username is reserved. Please choose another."
        
        if User.objects.filter(username__iexact=username).exclude(id=request.user.id if request else None).exists():
            return False, "Username already taken. Please choose another."
        
        if not phone_number or str(phone_number).strip().lower() == "none":
            return False, "Phone number is required."
        
        phone_number = str(phone_number).strip()
        if not phone_number.isdigit() or len(phone_number) != 10:
            return False, "Phone number must be exactly 10 digits."       
        
        if not phone_number.startswith(('98', '97', '99')):
            return False, "Phone number must start with a valid prefix (e.g., 98, 97)."
        
        if User.objects.filter(phone_number=phone_number).exclude(id=request.user.id if request else None).exists():
            return False, "This phone number is already registered."
        
        if not city_id or not country_id:
            return False, "City and country are required."
        
        if bio:
            bio = str(bio).strip()
            if len(bio) < 10:
                return False, "Bio must be at least 10 characters."
            if len(bio) > 500: 
                return False, "Bio must not exceed 500 characters."
        
        return True, None
    
    except Exception as e:
        return False, "Something went wrong. Please try again."

def validate_professional_info(hourly_rate, years_of_experience, expertise_level, availability, preferred_project_duration, communication_preference, selected_skills, 
    language_proficiencies):
    
    try:
        if not hourly_rate:
            return False, "Hourly rate is required."
            
        try:
            hourly_rate = float(hourly_rate)
            if hourly_rate < 100:
                return False, "Hourly rate should be at least 100 NPR."
            if hourly_rate > 10000:
                return False, "Hourly rate cannot exceed 10,000 NPR."
            if not hourly_rate.is_integer():
                return False, "Hourly rate should be a whole number."
        except ValueError:
            return False, "Please enter a valid number for hourly rate."
        
        if years_of_experience:
            try:
                years_of_experience = int(years_of_experience)
                if years_of_experience < 0:
                    return False, "Years of experience cannot be negative."
                if years_of_experience > 10:
                    return False, "Years of experience cannot exceed 50."
            except ValueError:
                return False, "Please enter a valid number for years of experience."
        
        if not expertise_level:
            return False, "Expertise level is required."
        
        if not availability:
            return False, "Availability is required."
        
        if not preferred_project_duration:
            return False, "Preferred project duration is required."
        
        if not communication_preference:
            return False, "Communication preference is required."

        if not selected_skills or len(selected_skills) == 0:
            return False, "At least one skill is required."
            
        if len(selected_skills) > 20:
            return False, "You can select maximum 20 skills."

        if not language_proficiencies or len(language_proficiencies) == 0:
            return False, "At least one language proficiency is required."

        return True, None
        
    except Exception as e:
        return False, "Something went wrong during validation. Please try again."

def validate_employment_data( company_name, job_title, employment_type, start_date, currently_working, end_date, country_id, city_id, 
    selected_skill_ids
    ):  
    
    if not company_name or company_name.strip() == '':
        return False, 'Company name is required.'
    
    if not job_title or job_title.strip() == '':
        return False, 'Job title is required.'
    
    if not employment_type or employment_type.strip() == '':
        return False, 'Employment type is required.'
    
    if not start_date or start_date.strip() == '':
        return False, 'Start date is required.'
    
    if not currently_working and (not end_date or end_date.strip() == ''):
        return False, 'End date is required if not currently working.'
    
    if not country_id or country_id.strip() == '':
        return False, 'Country is required.'
    
    if not city_id or city_id.strip() == '':
        return False, 'City is required.'
    
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m')
        
        if start_date_obj > datetime.now():
            return False, 'Start date cannot be in the future.'
        
        if not currently_working and end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m')
                
                if end_date_obj > datetime.now():
                    return False, 'End date cannot be in the future.'
                
                if end_date_obj < start_date_obj:
                   return False, 'End date must be after start date.'
                    
            except ValueError:
                return False, 'Invalid end date format.'
    except ValueError:
       return False, 'Invalid start date format.'
    
    if not selected_skill_ids or len(selected_skill_ids) == 0:
            return False, "At least one skill is required."
    
    return True, None

def validate_education_data(institution, degree, start_date, currently_studying, end_date, gpa):
    if not institution or institution.strip() == '':
        return False, 'Institution name is required.'
    
    if not degree or degree.strip() == '':
        return False, 'Degree is required.'
    
    if not start_date or start_date.strip() == '':
        return False, 'Start date is required.'
    
    if not currently_studying and (not end_date or end_date.strip() == ''):
        return False, 'End date is required if not currently studying.'
    
    if gpa and gpa.strip() != '':
        try:
            gpa_value = float(gpa)
            if gpa_value < 0 or gpa_value > 4:
                return False, 'GPA must be between 0 and 4.0'
        except ValueError:
            return False, 'Invalid GPA format. Please use numbers only (e.g., 3.5)'
    
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m')
        
        if start_date_obj > datetime.now():
            return False, 'Start date cannot be in the future.'
        
        if not currently_studying and end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m')
                
                if end_date_obj > datetime.now():
                    return False, 'End date cannot be in the future.'
                
                if end_date_obj < start_date_obj:
                    return False, 'End date must be after start date.'
                    
            except ValueError:
                return False, 'Invalid end date format.'
    except ValueError:
        return False, 'Invalid start date format.'
    
    return True, None

def validate_change_password_form(oldpassword, newpassword, confirmpassword, request=None):
    try:
        
        if not oldpassword or not newpassword or not confirmpassword:
            return False, 'All fields are required.'
        
        if not request.user.check_password(oldpassword):
            return False, 'Your old password was entered incorrectly.'
        
        if ' ' in newpassword or ' ' in confirmpassword:
            return False, 'Password should not contain spaces.'
        
        if newpassword != confirmpassword:
            return False, 'Password do not match.'
    
        if len(newpassword) < 8:
            return False, "Password must be at least 8 characters long."
        
        if not re.search(r'[A-Z]', newpassword):
            return False, "Password must contain at least one uppercase letter."
        
        if not re.search(r'[0-9]', newpassword):
            return False, "Password must contain at least one number."
        
        if not re.search(r'[@$!%*?&]', newpassword):
            return False, "Password must contain at least one special character."
        
    except Exception as e:
        return False, "Something went wrong. Please try again."
    
    return True, None

def validate_urls(portfolio_url=None, github_url=None, linkedin_url=None):
    try:
        url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        
        if portfolio_url:
            if not re.match(url_regex, portfolio_url):
                return False, "Please enter a valid portfolio URL (e.g., https://example.com)"
            
        if github_url:
            if not re.match(url_regex, github_url):
                return False, "Please enter a valid GitHub URL (e.g., https://github.com/username)"
            if not github_url.lower().startswith(('http://github.com/', 'https://github.com/', 'http://www.github.com/', 'https://www.github.com/')):
                return False, "Please enter a valid GitHub URL starting with 'https://github.com/'"
            
        if linkedin_url:
            if not re.match(url_regex, linkedin_url):
                return False, "Please enter a valid LinkedIn URL (e.g., https://linkedin.com/in/username)"
            if not linkedin_url.lower().startswith(('http://linkedin.com/', 'https://linkedin.com/', 'http://www.linkedin.com/', 'https://www.linkedin.com/')):
                return False, "Please enter a valid LinkedIn URL starting with 'https://linkedin.com/'"
            
        return True, None
    
    except Exception as e:
        return False, "Something went wrong. Please try again."

