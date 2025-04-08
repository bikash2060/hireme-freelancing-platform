from django.db import models
from clientprofile.models import Client

class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "skill"

class ProjectCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "project_category"

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.ManyToManyField(Skill, related_name='projects')
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    
    is_fixed_price = models.BooleanField(default=True, verbose_name="Fixed Price Project")
    fixed_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Published'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    estimated_duration = models.IntegerField(help_text="Duration in weeks")

    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ]
    experience_level = models.CharField(max_length=15, choices=EXPERIENCE_CHOICES, default='entry')    
    attachment = models.FileField(upload_to='project_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "project"
    
 
 
    
    


