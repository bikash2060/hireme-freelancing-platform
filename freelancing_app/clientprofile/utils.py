def validate_username(username):
    reserved_words = {"admin", "root", "user", "support"}
    
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

def validate_personal_info(first_name, last_name, phone_number, languages):
    
    if not first_name or not last_name or not phone_number or not languages:
        return False, "All fields are required."
    
    if ' ' in first_name or ' ' in last_name:
        return False, "First name and Last name cannot contain spaces."
    
    if not phone_number.isdigit() or len(phone_number) != 10:
         return False, "Phone number should be exactly 10 digits."
    
    return True, ""