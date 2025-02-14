from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    last_login = None

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"

class Client(models.Model):
    client_ID = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    languages = models.CharField(max_length=255, blank=True, null=True)  
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Client: {self.user.username}"
    
    class Meta:
        db_table = "client"

class Freelancer(models.Model):
    freelancer_ID = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    skills = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Freelancer: {self.user.username}"
    
    class Meta:
        db_table = "freelancer"
        