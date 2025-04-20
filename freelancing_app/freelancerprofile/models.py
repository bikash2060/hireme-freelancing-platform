from django.db import models
from accounts.models import User, City, Country
from projects.models import Skill

class Language(models.Model):
    """Represents a language that freelancers can speak"""
    code = models.CharField(max_length=10, unique=True, help_text="ISO language code")
    name = models.CharField(max_length=100, help_text="Full language name")
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"

class FreelanceServiceCategory(models.Model):
    """
    Represents popular skill-based service categories for homepage.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    icon_class = models.CharField(max_length=100, null=True, blank=True)  
    skills = models.ManyToManyField(Skill, related_name='service_categories')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "freelance_service_category"

class Freelancer(models.Model):
    """Main profile model for freelancers with professional information"""

    class ExpertiseLevel(models.TextChoices):
        ENTRY = 'entry', 'Entry Level'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        EXPERT = 'expert', 'Expert'

    class Availability(models.TextChoices):
        FULL_TIME = 'full-time', 'Full-time'
        PART_TIME = 'part-time', 'Part-time'
        NOT_AVAILABLE = 'not-available', 'Not Available'

    class ProjectDuration(models.TextChoices):
        SHORT = 'short', 'Less than 1 month'
        MEDIUM = 'medium', '1-3 months'
        LONG = 'long', '3+ months'

    class CommunicationPreference(models.TextChoices):
        EMAIL = 'email', 'Email'
        PHONE = 'phone', 'Phone'
        CHAT = 'chat', 'Chat'
        
    class BadgeChoices(models.TextChoices):
        TOP_RATED = 'top_rated', 'Top Rated'
        PRO_VERIFIED = 'pro_verified', 'Pro Verified'
        RISING_TALENT = 'rising_talent', 'Rising Talent'

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='freelancer_profile'
    )
    
    # Professional Information
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text="Total years of professional experience"
    )
    professional_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Professional title/headline (e.g., Full-Stack Developer)"
    )
    expertise_level = models.CharField(
        max_length=20,
        choices=ExpertiseLevel.choices,
        blank=True,
        help_text="Skill level in their field"
    )
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        blank=True,
        help_text="Current work availability status"
    )
    preferred_project_duration = models.CharField(
        max_length=20,
        choices=ProjectDuration.choices,
        blank=True,
        help_text="Preferred engagement duration"
    )
    communication_preference = models.CharField(
        max_length=20,
        choices=CommunicationPreference.choices,
        blank=True,
        help_text="Preferred communication method"
    )

    # Portfolio Links
    portfolio_link = models.URLField(
        blank=True,
        help_text="Link to portfolio website"
    )
    github_link = models.URLField(
        blank=True,
        help_text="Link to GitHub profile"
    )
    linkedin_link = models.URLField(
        blank=True,
        help_text="Link to LinkedIn profile"
    )

    # Relationships
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='freelancers',
        help_text="Skills possessed by the freelancer"
    )
    is_featured = models.BooleanField(default=False, help_text="Manually mark a freelancer as featured")
    
    badge = models.CharField(
        max_length=20,
        choices=BadgeChoices.choices,
        blank=True,
        help_text="Badge earned by the freelancer"
    )

    def __str__(self):
        return f"Freelancer: {self.user.username}"

    class Meta:
        db_table = "freelancer"
        verbose_name = "Freelancer Profile"
        verbose_name_plural = "Freelancer Profiles"


class FreelancerLanguage(models.Model):
    """Represents a language a freelancer speaks and their proficiency level"""

    class Proficiency(models.IntegerChoices):
        BASIC = 1, 'Basic'
        CONVERSATIONAL = 2, 'Conversational'
        FLUENT = 3, 'Fluent'
        ADVANCED = 4, 'Advanced'
        NATIVE = 5, 'Native/Bilingual'

    freelancer = models.ForeignKey(
        Freelancer,
        on_delete=models.CASCADE,
        related_name='languages'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='freelancers'
    )
    proficiency = models.IntegerField(
        choices=Proficiency.choices,
        help_text="Language proficiency level"
    )

    class Meta:
        db_table = "freelancer_language"
        unique_together = ('freelancer', 'language')
        verbose_name = "Freelancer Language"
        verbose_name_plural = "Freelancer Languages"

    def __str__(self):
        return f"{self.freelancer.user.username} - {self.language.name} ({self.get_proficiency_display()})"


class WorkExperience(models.Model):
    """Represents a freelancer's professional work experience"""

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full-time', 'Full-time'
        PART_TIME = 'part-time', 'Part-time'
        CONTRACT = 'contract', 'Contract'
        FREELANCE = 'freelance', 'Freelance'
        INTERNSHIP = 'internship', 'Internship'

    freelancer = models.ForeignKey(
        Freelancer,
        on_delete=models.CASCADE,
        related_name='work_experiences'
    )
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    # Location Information
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Skills used in this position
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='work_experiences'
    )

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    class Meta:
        db_table = 'work_experience'
        ordering = ['-start_date']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"


class Education(models.Model):
    """Represents a freelancer's educational background"""

    class DegreeType(models.TextChoices):
        HIGH_SCHOOL = 'high_school', 'High School Diploma'
        ASSOCIATE = 'associate', 'Associate Degree'
        BACHELOR = 'bachelor', "Bachelor's Degree"
        MASTER = 'master', "Master's Degree"
        DOCTORATE = 'phd', "Doctorate (PhD)"
        DIPLOMA = 'diploma', 'Diploma'
        CERTIFICATE = 'certificate', 'Certificate'
        MBA = 'mba', 'MBA'
        OTHER = 'other', 'Other'

    freelancer = models.ForeignKey(
        Freelancer,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    institution = models.CharField(max_length=200)
    degree = models.CharField(
        max_length=20,
        choices=DegreeType.choices,
        default=DegreeType.BACHELOR
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_studying = models.BooleanField(default=False)
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Grade Point Average (0.00-4.00 scale)"
    )

    def __str__(self):
        return f"{self.get_degree_display()} from {self.institution}"

    class Meta:
        db_table = 'education'
        verbose_name = "Education"
        verbose_name_plural = "Education Records"
        ordering = ['-start_date']