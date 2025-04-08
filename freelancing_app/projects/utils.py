from .models import *
import os

def validate_project_data(
        title, 
        category_id, 
        experience_level, 
        estimated_duration,
        is_price_range,
        fixed_budget,
        budget_min,
        budget_max,
        description,
        selected_skills,
        attachments,
        request=None
    ):
    try:
        if not title or str(title).strip().lower() == "none":
            return False, "Project title is required."
        
        title = str(title).strip()
        if len(title) < 10:
            return False, "Title must be at least 10 characters long."
        if len(title) > 50:
            return False, "Title must not exceed 50 characters."
        
        if not category_id:
            return False, "Project category is required."
        try:
            category = ProjectCategory.objects.get(id=category_id)
        except ProjectCategory.DoesNotExist:
            return False, "Invalid project category selected."
        
        if not experience_level:
            return False, "Please select a experience level."
        
        try:
            duration = int(estimated_duration)
            if duration < 1 or duration > 104:
                return False, "Duration must be between 1-104 weeks."
        except (ValueError, TypeError):
            return False, "Please enter a valid duration in weeks."
        
        if is_price_range:
            if not budget_min or not budget_max:
                return False, "Both minimum and maximum budget are required for price range."
            
            try:
                min_val = float(budget_min)
                max_val = float(budget_max)
                if min_val < 1000:
                    return False, "Minimum budget must be at least NPR 1000."
                if max_val < 1000:
                    return False, "Maximum budget must be at least NPR 1000."
                if min_val >= max_val:
                    return False, "Minimum budget must be less than maximum budget."
            except (ValueError, TypeError):
                return False, "Please enter valid budget amounts."
        else:
            if not fixed_budget:
                return False, "Fixed budget amount is required."
            try:
                if float(fixed_budget) < 1000:
                    return False, "Budget must be at least NPR 1000."
            except (ValueError, TypeError):
                return False, "Please enter a valid fixed budget amount."
        
        if not description or str(description).strip().lower() == "none":
            return False, "Project description is required."
        
        description = str(description).strip()
        if len(description) < 50:
            return False, "Description must be at least 50 characters."
        if len(description) > 2000:
            return False, "Description must not exceed 500 characters."
        
        if not selected_skills:
            return False, "At least one skill is required."
        
        try:
            valid_skills = Skill.objects.filter(id__in=selected_skills).count()
            if valid_skills != len(selected_skills):
                return False, "One or more selected skills are invalid."
        except Exception:
            return False, "Invalid skill selection."
        
        if attachments:
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            max_size = 5 * 1024 * 1024  
            
            for attachment in attachments:
                file_extension = os.path.splitext(attachment.name)[1].lower()
                if file_extension not in valid_extensions:
                    return False, "Invalid file type. Only PDF, DOC, JPG, PNG are allowed."
                
                if attachment.size > max_size:
                    return False, "File exceeds 5MB size limit."
                        
        return True, None
    
    except Exception as e:
        return False, "Something went wrong during validation. Please try again."