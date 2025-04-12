from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest
from accounts.models import User
from typing import Optional, Tuple, Dict, Any
from django.conf import settings
from datetime import datetime
import os
import re

class Validator:
    """Base validator class with common validation methods"""
    
    @classmethod
    def validate_required(cls, value: Any, field_name: str) -> Tuple[bool, str]:
        """Validate that a required field has a value"""
        if not value:
            return False, f"{field_name.replace('_', ' ').title()} is required."
        return True, ""
    
    @classmethod
    def validate_length(cls, value: str, min_len: int, max_len: int, field_name: str) -> Tuple[bool, str]:
        """Validate string length constraints"""
        if len(value) < min_len:
            return False, f"{field_name.replace('_', ' ').title()} must be at least {min_len} characters."
        if len(value) > max_len:
            return False, f"{field_name.replace('_', ' ').title()} must not exceed {max_len} characters."
        return True, ""

class ProfileValidator(Validator):
    """Handles validation of profile data"""
    
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    VALID_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']
    NAME_REGEX = r'^[a-zA-Z\s\-\.\']+$'
    USERNAME_REGEX = r'^[a-zA-Z0-9_\.]+$'
    
    @classmethod
    def validate_profile_image(cls, image: Optional[UploadedFile]) -> Tuple[bool, str]:
        """Validate profile image file"""
        if not image:
            return True, ""
            
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in cls.VALID_IMAGE_EXTENSIONS:
            return False, "Only JPG, PNG, or JPEG file types are allowed."
        
        if image.size > cls.MAX_IMAGE_SIZE:
            return False, "File size exceeds the 10MB limit."
            
        try:
            from PIL import Image
            Image.open(image).verify()
        except ImportError:
            return False, "Image processing library not available."
        except Exception:
            return False, "Invalid image file."
            
        return True, ""

    @classmethod
    def validate_full_name(cls, name: str) -> Tuple[bool, str]:
        """Validate full name format"""
        name = str(name).strip()
        
        if not name or name.lower() == "none":
            return False, "Full name is required"
            
        valid, message = cls.validate_length(name, 3, 50, "full name")
        if not valid:
            return valid, message
            
        if name.isdigit():
            return False, "Full name cannot be only numbers."
            
        if name[0].isdigit():
            return False, "Full name cannot start with a number."
            
        if not re.match(cls.NAME_REGEX, name):
            return False, "Full name contains invalid characters."
            
        return True, ""

    @classmethod
    def validate_username(cls, username: str, request: Optional[HttpRequest] = None) -> Tuple[bool, str]:
        """Validate username format and uniqueness"""
        username = str(username).strip()
        
        valid, message = cls.validate_required(username, "username")
        if not valid:
            return valid, message
            
        if " " in username:
            return False, "Username cannot contain spaces."
            
        if username.isdigit():
            return False, "Username cannot be only numbers."
            
        if username[0].isdigit():
            return False, "Username cannot start with a number."
            
        valid, message = cls.validate_length(username, 5, 50, "username")
        if not valid:
            return valid, message
            
        if not re.match(cls.USERNAME_REGEX, username):
            return False, "Username can only contain letters, numbers, underscores."
            
        if username.lower() in settings.RESERVED_USERNAMES:
            return False, "This username is reserved. Please choose another."
            
        user_id = request.user.id if request and hasattr(request, 'user') else None
        if User.objects.filter(username__iexact=username).exclude(id=user_id).exists():
            return False, "Username already taken."
            
        return True, ""

    @classmethod
    def validate_phone_number(cls, phone: str, request: Optional[HttpRequest] = None) -> Tuple[bool, str]:
        """Validate phone number format and uniqueness"""
        phone = str(phone).strip()
        
        valid, message = cls.validate_required(phone, "phone number")
        if not valid:
            return valid, message
            
        if not phone.isdigit() or len(phone) != 10:
            return False, "Phone number must be exactly 10 digits."
            
        if not phone.startswith(('98', '97', '99')):
            return False, "Phone number must start with 98, 97 or 99."
            
        user_id = request.user.id if request and hasattr(request, 'user') else None
        if User.objects.filter(phone_number=phone).exclude(id=user_id).exists():
            return False, "Phone number already registered."
            
        return True, ""

    @classmethod
    def validate_bio(cls, bio: Optional[str]) -> Tuple[bool, str]:
        """Validate bio text length"""
        if not bio:
            return True, ""
            
        bio = str(bio).strip()
        return cls.validate_length(bio, 10, 500, "bio")

    @classmethod
    def validate_location(cls, city_id: Optional[int], country_id: Optional[int]) -> Tuple[bool, str]:
        """Validate location selection"""
        if not city_id or not country_id:
            return False, "City and country are required."
        return True, ""

    @classmethod
    def validate_user_data(
        cls, 
        profile_image: Optional[UploadedFile],
        full_name: str,
        username: str,
        phone_number: str,
        bio: str,
        city_id: Optional[int],
        country_id: Optional[int],
        request: HttpRequest
    ) -> Tuple[bool, str]:
        """Validate all user profile data"""
        validators = [
            (cls.validate_profile_image, (profile_image,)),
            (cls.validate_full_name, (full_name,)),
            (cls.validate_username, (username, request)),
            (cls.validate_phone_number, (phone_number, request)),
            (cls.validate_bio, (bio,)),
            (cls.validate_location, (city_id, country_id)),
        ]
        
        for validator, args in validators:
            valid, message = validator(*args)
            if not valid:
                return False, message
                
        return True, ""

class PasswordValidator(Validator):
    """Handles password validation"""
    
    @classmethod
    def validate_new_password(cls, password: str, confirm_password: str) -> Tuple[bool, str]:
        """Validate password requirements"""
        if ' ' in password or ' ' in confirm_password:
            return False, "Password should not contain spaces."
            
        if password != confirm_password:
            return False, "Passwords do not match."
            
        valid, message = cls.validate_length(password, 8, 128, "password")
        if not valid:
            return valid, message
            
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain an uppercase letter."
            
        if not re.search(r'[0-9]', password):
            return False, "Password must contain a number."
            
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain a special character (@$!%*?&)."
            
        return True, ""

    @classmethod
    def validate_change_password_form(
        cls,
        old_password: str,
        new_password: str,
        confirm_password: str,
        request: HttpRequest
    ) -> Tuple[bool, str]:
        """Validate password change form"""
        user = request.user
        if not user.check_password(old_password):
            return False, "Your old password was entered incorrectly."
            
        return cls.validate_new_password(new_password, confirm_password)