from django.db import models
from accounts.models import User, City, Country
from projects.models import Skill

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)  
    name = models.CharField(max_length=100)              
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "language"

class Freelancer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='freelancer_profile'
    )
    hourly_rate = models.IntegerField(default=0)
    skills = models.ManyToManyField(Skill, blank=True) 

    def __str__(self):
        return f"Freelancer: {self.user.username}"

    class Meta:
        db_table = "freelancer"
        
class FreelancerLanguage(models.Model):
    PROFICIENCY_LEVELS = (
        (1, 'Basic'),
        (2, 'Conversational'),
        (3, 'Fluent'),
        (4, 'Advanced'),
        (5, 'Native/Bilingual'),
    )
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    proficiency = models.IntegerField(choices=PROFICIENCY_LEVELS)
    
    class Meta:
        unique_together = ('freelancer', 'language')  
        db_table = "freelancer_language"
    
    def __str__(self):
        return f"{self.freelancer.user.username} - {self.language.name} ({self.get_proficiency_display()})"


class WorkExperience(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    class Meta:
        db_table = 'work_experience'
        ordering = ['-start_date']