from typing import Tuple, Optional, List, Union
from django.core.files.uploadedfile import UploadedFile
from projects.models import Project
import os
from datetime import datetime
from decimal import Decimal

class ProposalValidator:
    """Utility class for validating proposal data."""
    
    MIN_COVER_LETTER = 200
    MAX_COVER_LETTER = 3000
    MIN_PROPOSED_AMOUNT = 1000
    MIN_DURATION = 1
    MAX_DURATION = 104
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    MAX_APPROACH_LENGTH = 2000
    MAX_EXPERIENCE_LENGTH = 1500
    MAX_QUESTIONS_LENGTH = 500

    @classmethod
    def validate_proposal_data(
        cls,
        cover_letter: str,
        proposed_amount: Union[str, float],
        estimated_duration: Union[str, int],
        attachments: List[UploadedFile],
        project: Project,
        approach_methodology: Optional[str] = None,
        relevant_experience: Optional[str] = None,
        questions_for_client: Optional[str] = None,
        available_start_date: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate all proposal data fields."""
        validation_methods = [
            cls._validate_cover_letter,
            cls._validate_proposed_amount,
            cls._validate_duration,
            cls._validate_attachments,
            cls._validate_budget_against_project,
            cls._validate_approach_methodology,
            cls._validate_relevant_experience,
            cls._validate_questions_for_client,
            cls._validate_available_start_date,
        ]

        for method in validation_methods:
            is_valid, error_msg = method(
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                attachments=attachments,
                project=project,
                approach_methodology=approach_methodology,
                relevant_experience=relevant_experience,
                questions_for_client=questions_for_client,
                available_start_date=available_start_date
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
            proposed = Decimal(str(proposed_amount))
            
            if project.is_fixed_price:
                max_allowed = project.fixed_budget * Decimal('1.5')
                if proposed > max_allowed:
                    return False, f"Proposed amount exceeds allowed limit ({max_allowed})."
            else:
                max_allowed = project.budget_max * Decimal('1.5')
                if proposed > max_allowed:
                    return False, f"Proposed amount exceeds allowed limit ({max_allowed})."

                
            return True, None
        except (ValueError, TypeError) as e:
            print(f"[DEBUG] Error converting proposed amount: {e}")
            return False, f"Invalid proposed amount. Please enter a valid number. Error: {str(e)}"

    @classmethod
    def _validate_approach_methodology(cls, approach_methodology: Optional[str] = None, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate approach and methodology field."""
        if approach_methodology and len(approach_methodology.strip()) > cls.MAX_APPROACH_LENGTH:
            return False, f"Approach & methodology must not exceed {cls.MAX_APPROACH_LENGTH} characters."
        return True, None

    @classmethod
    def _validate_relevant_experience(cls, relevant_experience: Optional[str] = None, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate relevant experience field."""
        if relevant_experience and len(relevant_experience.strip()) > cls.MAX_EXPERIENCE_LENGTH:
            return False, f"Relevant experience must not exceed {cls.MAX_EXPERIENCE_LENGTH} characters."
        return True, None

    @classmethod
    def _validate_questions_for_client(cls, questions_for_client: Optional[str] = None, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate questions for client field."""
        if questions_for_client and len(questions_for_client.strip()) > cls.MAX_QUESTIONS_LENGTH:
            return False, f"Questions for client must not exceed {cls.MAX_QUESTIONS_LENGTH} characters."
        return True, None

    @classmethod
    def _validate_available_start_date(cls, available_start_date: Optional[str] = None, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate available start date field."""
        if not available_start_date or available_start_date.strip() == "":
            return True, None
            
        try:
            input_date = datetime.strptime(available_start_date.strip(), '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if input_date < today:
                return False, "Available start date cannot be in the past."
            return True, None
        except ValueError:
            return False, "Please enter a valid date in YYYY-MM-DD format."