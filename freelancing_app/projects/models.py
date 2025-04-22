from django.utils.translation import gettext_lazy as _
from clientprofile.models import Client
from django.db import models

class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "skill"
        
class ProjectSkill(models.Model):
    class SkillLevel(models.TextChoices):
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='project_skills')
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE, related_name='project_skills')
    level = models.CharField(
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.INTERMEDIATE
    )

    class Meta:
        unique_together = ('project', 'skill')
        db_table = 'project_skill'

    def __str__(self):
        return f"{self.project.title} - {self.skill.name} ({self.get_level_display()})"

class ProjectCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "project_category"

class Project(models.Model):
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        HIRING = 'hiring', _('Reviewing Proposals')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        
    class ExpertiseLevel(models.TextChoices):
        ENTRY = 'entry', _('Entry Level')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        EXPERT = 'expert', _('Expert')
        
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    key_requirements = models.TextField(
        blank=True,
        help_text="List of key requirements, one per line"
    )
    additional_info = models.TextField(
        blank=True,
        help_text="Any extra information or project guidelines"
    )
    skills_required = models.ManyToManyField(
        Skill,
        through='ProjectSkill',
        related_name='projects'
    )
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    
    is_fixed_price = models.BooleanField(default=True, verbose_name="Fixed Price Project")
    fixed_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    estimated_duration = models.IntegerField(help_text="Duration in weeks")

    experience_level = models.CharField(max_length=15, choices=ExpertiseLevel.choices, default=ExpertiseLevel.ENTRY)    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "project"
    

class ProjectAttachment(models.Model):
    """Files attached to projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_attachments')  
    file = models.FileField(upload_to='project_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.project.title}"
    
    class Meta:
        db_table = "project_attachment"
 
    
    


