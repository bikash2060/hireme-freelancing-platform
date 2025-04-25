from django.core.files.uploadedfile import UploadedFile
from typing import Optional, List, Tuple, Union
from .models import ProjectCategory, Skill
from django.http import HttpRequest
import os

class ProjectValidator:
    """Utility class for validating project data."""
    
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 50
    MIN_DURATION = 1
    MAX_DURATION = 104
    MIN_BUDGET = 1000
    MIN_DESCRIPTION_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

    @classmethod
    def validate_project_data(
        cls,
        title: str,
        category_id: int,
        experience_level: str,
        estimated_duration: Union[int, str],
        is_price_range: bool,
        fixed_budget: Optional[Union[float, str]],
        budget_min: Optional[Union[float, str]],
        budget_max: Optional[Union[float, str]],
        description: str,
        key_requirements: str,
        additional_info: str,
        selected_skills: List[int],
        attachments: Optional[List[UploadedFile]],
        request: Optional[HttpRequest] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate all project data fields."""
        validation_methods = [
            cls._validate_title,
            cls._validate_category,
            cls._validate_experience_level,
            cls._validate_duration,
            cls._validate_budget,
            cls._validate_description,
            cls._validate_key_requirements,
            cls._validate_additional_info,
            cls._validate_skills,
            cls._validate_attachments,
        ]

        for method in validation_methods:
            is_valid, error_msg = method(
                title=title,
                category_id=category_id,
                experience_level=experience_level,
                estimated_duration=estimated_duration,
                is_price_range=is_price_range,
                fixed_budget=fixed_budget,
                budget_min=budget_min,
                budget_max=budget_max,
                description=description,
                key_requirements=key_requirements,
                additional_info=additional_info,
                selected_skills=selected_skills,
                attachments=attachments,
            )
            if not is_valid:
                return False, error_msg

        return True, None

    @classmethod
    def _validate_title(cls, title: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate project title."""
        if not title or str(title).strip().lower() == "none":
            return False, "Project title is required."
        
        title = str(title).strip()
        if len(title) < cls.MIN_TITLE_LENGTH:
            return False, f"Title must be at least {cls.MIN_TITLE_LENGTH} characters long."
        if len(title) > cls.MAX_TITLE_LENGTH:
            return False, f"Title must not exceed {cls.MAX_TITLE_LENGTH} characters."
        return True, None

    @classmethod
    def _validate_category(cls, category_id: int, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate project category."""
        if not category_id:
            return False, "Project category is required."
        try:
            ProjectCategory.objects.get(id=category_id)
            return True, None
        except ProjectCategory.DoesNotExist:
            return False, "Invalid project category selected."

    @classmethod
    def _validate_experience_level(cls, experience_level: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate experience level."""
        if not experience_level:
            return False, "Please select an experience level."
        return True, None

    @classmethod
    def _validate_duration(cls, estimated_duration: Union[int, str], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate project duration."""
        try:
            duration = int(estimated_duration)
            if duration < cls.MIN_DURATION or duration > cls.MAX_DURATION:
                return False, f"Duration must be between {cls.MIN_DURATION}-{cls.MAX_DURATION} weeks."
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid duration in weeks."

    @classmethod
    def _validate_budget(
        cls,
        is_price_range: bool,
        fixed_budget: Optional[Union[float, str]],
        budget_min: Optional[Union[float, str]],
        budget_max: Optional[Union[float, str]],
        **kwargs
    ) -> Tuple[bool, Optional[str]]:
        """Validate project budget based on pricing type."""
        if is_price_range:
            return cls._validate_price_range(budget_min, budget_max)
        return cls._validate_fixed_budget(fixed_budget)

    @classmethod
    def _validate_price_range(
        cls,
        budget_min: Optional[Union[float, str]],
        budget_max: Optional[Union[float, str]],
    ) -> Tuple[bool, Optional[str]]:
        """Validate price range budget."""
        if not budget_min or not budget_max:
            return False, "Both minimum and maximum budget are required for price range."
        
        try:
            min_val = float(budget_min)
            max_val = float(budget_max)
            
            if min_val < cls.MIN_BUDGET or max_val < cls.MIN_BUDGET:
                return False, f"Budget must be at least NPR {cls.MIN_BUDGET}."
            if min_val >= max_val:
                return False, "Minimum budget must be less than maximum budget."
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter valid budget amounts."

    @classmethod
    def _validate_fixed_budget(cls, fixed_budget: Optional[Union[float, str]]) -> Tuple[bool, Optional[str]]:
        """Validate fixed budget."""
        if not fixed_budget:
            return False, "Fixed budget amount is required."
        try:
            if float(fixed_budget) < cls.MIN_BUDGET:
                return False, f"Budget must be at least NPR {cls.MIN_BUDGET}."
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid fixed budget amount."

    @classmethod
    def _validate_description(cls, description: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate project description."""
        if not description or str(description).strip().lower() == "none":
            return False, "Project description is required."
        
        description = str(description).strip()
        if len(description) < cls.MIN_DESCRIPTION_LENGTH:
            return False, f"Description must be at least {cls.MIN_DESCRIPTION_LENGTH} characters."
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            return False, f"Description must not exceed {cls.MAX_DESCRIPTION_LENGTH} characters."
        return True, None
    
    @classmethod
    def _validate_key_requirements(cls, key_requirements: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate key requirements."""
        if not key_requirements or str(key_requirements).strip().lower() == "none":
            return True, None  # This field is optional
        
        key_requirements = str(key_requirements).strip()
        if len(key_requirements) > 500:
            return False, "Key requirements must not exceed 500 characters."
        return True, None

    @classmethod
    def _validate_additional_info(cls, additional_info: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate additional info."""
        if not additional_info or str(additional_info).strip().lower() == "none":
            return True, None  # This field is optional
        
        additional_info = str(additional_info).strip()
        if len(additional_info) > 500:
            return False, "Additional information must not exceed 500 characters."
        return True, None

    @classmethod
    def _validate_skills(cls, selected_skills: List[int], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate selected skills."""
        if not selected_skills:
            return False, "At least one skill is required."
        
        try:
            valid_skills_count = Skill.objects.filter(id__in=selected_skills).count()
            if valid_skills_count != len(selected_skills):
                return False, "One or more selected skills are invalid."
            return True, None
        except Exception:
            return False, "Invalid skill selection."

    @classmethod
    def _validate_attachments(cls, attachments: Optional[List[UploadedFile]], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate project attachments."""
        if not attachments:
            return True, None
            
        for attachment in attachments:
            # Validate file extension
            file_extension = os.path.splitext(attachment.name)[1].lower()
            if file_extension not in cls.ALLOWED_FILE_EXTENSIONS:
                return False, "Invalid file type. Only PDF, DOC, JPG, PNG are allowed."
            
            # Validate file size
            if attachment.size > cls.MAX_FILE_SIZE:
                return False, "File exceeds 5MB size limit."
        
        return True, None