from django.conf import settings
from accounts.models import User
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

def validate_professional_info(city, hourly_rate, selected_skills, language_proficiencies):
    try:
        if not city or str(city).strip().lower() == "none":
            return False, "City is required."
        
        if not hourly_rate or str(hourly_rate).strip().lower() == "none":
            return False, "Hourly rate is required."
            
        try:
            hourly_rate = float(hourly_rate)
            if hourly_rate < 0:
                return False, "Hourly rate cannot be negative."
            if hourly_rate > 100000:
                return False, "Hourly rate exceeds the maximum limit of 10,000 NPR."
        except ValueError:
            return False, "Please enter a valid number for hourly rate."
        
        if not selected_skills or len(selected_skills) == 0:
            return False, "At least one skill is required."
        
        if not language_proficiencies or len(language_proficiencies) == 0:
            return False, "At least one language proficiency is required."
            
        return True, None
        
    except Exception as e:
        return False, f"Something went wrong. Please try again. Error: {str(e)}"