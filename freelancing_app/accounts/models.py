from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set', 
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  
        blank=True,
    )

    class Meta:
        db_table = "User"
    
    def __str__(self):
        return self.username



class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='clients/', blank=True, null=True)

    class Meta:
        db_table = "Client"

    def __str__(self):
        return self.user.username  


class Freelancer(models.Model):
    freelancer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    profile_picture = models.ImageField(upload_to='freelancers/', blank=True, null=True)
    experience = models.IntegerField(help_text="Years of experience")
    language = models.CharField(max_length=255, blank=True, null=True)
    video_introduction = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "Freelancer"

    def __str__(self):
        return self.user.username  