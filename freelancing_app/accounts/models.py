from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now, timedelta

def default_expired_time():
    return now() + timedelta(minutes=2)

class OTPCode(models.Model):
    otp_id = models.AutoField(primary_key=True)
    otp_code = models.CharField(max_length=6)
    email = models.EmailField()
    otp_generated_time = models.DateTimeField(default=now)
    otp_expired_time = models.DateTimeField(default=default_expired_time)
    
    class Meta:
        db_table = "otp_code"

    def is_valid(self):
        """Check if the OTP is still valid."""
        return now() <= self.otp_expired_time

    def __str__(self):
        return f"OTP for {self.email}"

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

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
    
    