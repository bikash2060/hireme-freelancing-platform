import os
from datetime import datetime

def validate_form(project_name, project_description, project_image, project_budget, project_duration, skills_select, project_category):
    # Strip spaces before validation
    project_name = project_name.strip()
    project_description = project_description.strip()

    # Check for empty fields
    if not project_name:
        return False, 'Project name is required.'
    if not project_description:
        return False, 'Project description is required.'
    if not project_budget:
        return False, 'Project budget is required.'
    if not project_duration:
        return False, 'Project duration is required.'
    if not skills_select:
        return False, 'At least one skill must be selected.'
    if not project_category:
        return False, 'Project category is required.'

    # Validate project name length
    if len(project_name) < 5 or len(project_name) > 50:
        return False, 'Project name must be between 5 and 50 characters.'

    # Validate project description length
    if len(project_description) < 50 or len(project_description) > 500:
        return False, 'Project description must be between 50 and 300 characters.'

    # Validate project image (if any)
    if project_image:
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif']
        file_extension = os.path.splitext(project_image.name)[1].lower()

        if file_extension not in valid_extensions:
            return False, 'Only JPG, PNG, JPEG, or GIF file types are allowed.'

        # Adjusted max size to 20MB
        max_size = 20 * 1024 * 1024  # 20MB
        if project_image.size > max_size:
            return False, 'File size exceeds the 20MB limit.'

    # Validate project budget
    try:
        project_budget = float(project_budget)
        if project_budget <= 0:
            return False, 'Project budget must be greater than zero.'
    except ValueError:
        return False, 'Project budget must be a valid number.'

    # Validate project duration
    try:
        duration_date = datetime.strptime(project_duration, '%Y-%m-%d').date()
        if duration_date < datetime.today().date():
            return False, 'Project duration must not be in the past.'
    except ValueError:
        return False, 'Invalid date format for project duration. Please use YYYY-MM-DD.'

    # Validate skills selection (ensure skills are valid integers if passed as IDs)
    try:
        if not all(isinstance(int(skill), int) for skill in skills_select):
            return False, 'Invalid skill selection. Please select valid skills.'
    except ValueError:
        return False, 'Invalid skill selection. Please select valid skills.'

    # Validate project category
    try:
        if not isinstance(int(project_category), int):
            return False, 'Invalid project category. Please select a valid category.'
    except ValueError:
        return False, 'Invalid project category. Please select a valid category.'

    return True, ''  # Return True if all validations pass
