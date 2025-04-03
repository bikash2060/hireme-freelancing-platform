from django.conf import settings
from accounts.models import User
from datetime import datetime
import os
import re

def validate_user_data(profile_image, full_name, username, phone_number, bio, request=None):
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
        
        if len(full_name) > 20: 
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
        
        if len(username) > 15:
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
        
        if bio:
            bio = str(bio).strip()
            if len(bio) < 10:
                return False, "Bio must be at least 10 characters."
            if len(bio) > 500: 
                return False, "Bio must not exceed 500 characters."
        
        return True, None
    
    except Exception as e:
        return False, "Something went wrong. Please try again."

def validate_professional_info(city_id, country_id, hourly_rate, selected_skills, language_proficiencies):
    try:
        if not country_id:
            return False, "Country is required."

        if not city_id:
            return False, "City is required."

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

        if not selected_skills or len(selected_skills) == 0:
            return False, "At least one skill is required."
            
        if len(selected_skills) > 20:
            return False, "You can select maximum 20 skills."

        if not language_proficiencies or len(language_proficiencies) == 0:
            return False, "At least one language proficiency is required."

        return True, None
        
    except Exception as e:
        return False, "Something went wrong during validation. Please try again."

def validate_employment_data(
        company_name, job_title, employment_type, start_date, 
        currently_working, end_date, country_id, city_id, selected_skill_ids
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
    
