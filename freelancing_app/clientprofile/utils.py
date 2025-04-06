from django.conf import settings
from accounts.models import User
from datetime import datetime
import os
import re

def validate_user_data(profile_image, full_name, username, phone_number, city_id, country_id, bio, request=None):
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
        
        if len(full_name) >50: 
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
        
        if len(username) > 50:
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
        
        if not country_id:
            return False, "Country is required."

        if not city_id:
            return False, "City is required."
        
        if bio:
            bio = str(bio).strip()
            if len(bio) < 10:
                return False, "Bio must be at least 10 characters."
            if len(bio) > 500: 
                return False, "Bio must not exceed 500 characters."
        
        return True, None
    
    except Exception as e:
        return False, "Something went wrong. Please try again."


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