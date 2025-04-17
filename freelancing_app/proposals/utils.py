from typing import Tuple, Optional, List, Union
from django.core.files.uploadedfile import UploadedFile
from projects.models import Project
import os

class ProposalValidator:
    """Utility class for validating proposal data."""
    
    MIN_COVER_LETTER = 100
    MAX_COVER_LETTER = 2000
    MIN_PROPOSED_AMOUNT = 1000
    MIN_DURATION = 1
    MAX_DURATION = 104
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

    @classmethod
    def validate_proposal_data(
        cls,
        cover_letter: str,
        proposed_amount: Union[str, float],
        estimated_duration: Union[str, int],
        attachments: List[UploadedFile],
        project: Project
    ) -> Tuple[bool, Optional[str]]:
        """Validate all proposal data fields."""
        validation_methods = [
            cls._validate_cover_letter,
            cls._validate_proposed_amount,
            cls._validate_duration,
            cls._validate_attachments,
            cls._validate_budget_against_project,
        ]

        for method in validation_methods:
            is_valid, error_msg = method(
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                attachments=attachments,
                project=project
            )
            if not is_valid:
                return False, error_msg

        return True, None

    @classmethod
    def _validate_cover_letter(cls, cover_letter: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate cover letter content."""
        if not cover_letter or str(cover_letter).strip().lower() == "none":
            return False, "Cover letter is required."
        
        cover_letter = str(cover_letter).strip()
        if len(cover_letter) < cls.MIN_COVER_LETTER:
            return False, f"Cover letter must be at least {cls.MIN_COVER_LETTER} characters."
        if len(cover_letter) > cls.MAX_COVER_LETTER:
            return False, f"Cover letter must not exceed {cls.MAX_COVER_LETTER} characters."
        return True, None

    @classmethod
    def _validate_proposed_amount(cls, proposed_amount: Union[str, float], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate proposed amount."""
        if not proposed_amount:
            return False, "Proposed amount is required."
        
        try:
            amount = float(proposed_amount)
            if amount < cls.MIN_PROPOSED_AMOUNT:
                return False, f"Proposed amount must be at least NPR {cls.MIN_PROPOSED_AMOUNT}."
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid proposed amount."

    @classmethod
    def _validate_duration(cls, estimated_duration: Union[str, int], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate estimated duration."""
        if not estimated_duration:
            return False, "Estimated duration is required."
        
        try:
            duration = int(estimated_duration)
            if duration < cls.MIN_DURATION or duration > cls.MAX_DURATION:
                return False, f"Duration must be between {cls.MIN_DURATION}-{cls.MAX_DURATION} weeks."
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid duration in weeks."

    @classmethod
    def _validate_attachments(cls, attachments: List[UploadedFile], **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate proposal attachments."""
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

    @classmethod
    def _validate_budget_against_project(cls, proposed_amount: Union[str, float], project: Project, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate proposed amount against project budget constraints."""
        try:
            proposed = float(proposed_amount)
            
            if project.is_fixed_price:
                if proposed > project.fixed_budget * 1.5:  # Allow 50% over fixed budget
                    return False, "Your proposed amount is significantly higher than the client's budget."
            else:
                if proposed > project.budget_max * 1.5:  # Allow 50% over max budget
                    return False, "Your proposed amount is significantly higher than the client's maximum budget."
                
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid proposed amount."