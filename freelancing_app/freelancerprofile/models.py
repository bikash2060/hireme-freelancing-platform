from django.db import models
from accounts.models import Freelancer

class Education(models.Model):
    education_id = models.BigAutoField(primary_key=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name="educations")
    education_level = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)  
    location = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='company_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.degree} at {self.institution} ({self.freelancer.user.username})"
    
    class Meta:
        db_table = "education"