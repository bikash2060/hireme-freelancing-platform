from django.db import models
from accounts.models import Client

class Company(models.Model):
    logo = models.ImageField(upload_to='company_images/', null=True, blank=True) 
    name = models.CharField(max_length=255, null=True, blank=True)  
    position = models.CharField(max_length=255, null=True, blank=True)  
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True)  
    location = models.CharField(max_length=255, null=True, blank=True) 
    url = models.URLField(max_length=500, null=True, blank=True) 
    client= models.ForeignKey(Client, on_delete=models.CASCADE, related_name="companies")

    def __str__(self):
        return self.name or "Unnamed Company"
    
    class Meta:
        db_table = "company"
