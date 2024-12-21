import os

def validate_username(username):
    reserved_words = {"admin", "root", "user", "support", "client", "freelancer"}
    
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
    if not profile_image:
        return False, "No file uploaded. Please upload a valid image."
    
    valid_extensions = ['.png', '.jpg', '.jpeg']
    file_extension = os.path.splitext(profile_image.name)[1].lower()
    
    if file_extension not in valid_extensions:
        return False, "Only JPG, PNG, or JPEG file types are allowed."
    
    max_size = 10 * 1024 * 1024  # 10 MB
    if profile_image.size > max_size:
        return False, "File size exceeds the 10MB limit."

    return True, "File is valid."

def validate_personal_info(first_name, middle_name, last_name, phone_number, bio):
    
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
    
    if bio and len(bio) > 500:
        return False, "Bio should not exceed 500 characters."
    
    return True, ""