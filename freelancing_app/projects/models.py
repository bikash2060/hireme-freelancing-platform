from django.db import models
from accounts.models import Client

class Project(models.Model):
    image = models.ImageField(upload_to='project_images/', null=True, blank=True, help_text="Project image")
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(help_text="Deadline of the project (in YYYY-MM-DD format)", null=True)  
    skills = models.CharField(max_length=255, help_text="Skills required for the project", null=True, blank=True)
    category = models.CharField(max_length=100, help_text="Category of the project", null=True, blank=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "project"
