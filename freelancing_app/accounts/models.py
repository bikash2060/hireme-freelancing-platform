from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now, timedelta
from django.db import models

def default_expired_time():
    """Returns datetime 3 minutes in the future for OTP expiration"""
    return now() + timedelta(minutes=3)


class Country(models.Model):
    """Model representing countries"""
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
        db_table = 'country'
    
    def __str__(self):
        return self.name
    

class City(models.Model):
    """Model representing cities with their country association"""
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        related_name='cities'
    )
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
        unique_together = ('name', 'country')
        db_table = 'city'
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    

class OTPCode(models.Model):
    """Model for storing One-Time Password codes"""
    
    id = models.AutoField(primary_key=True)
    otp_code = models.CharField(max_length=6)
    email = models.EmailField()
    otp_generated_time = models.DateTimeField(default=now)
    otp_expired_time = models.DateTimeField(default=default_expired_time)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = "otp_code"
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['otp_expired_time']),
        ]
        

class CustomUserManager(BaseUserManager):
    """Custom manager for the User model"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model extending AbstractBaseUser"""
    
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
        ('admin', 'Admin')
    ]
    
    AUTH_METHOD_CHOICES = [
        ('traditional', 'Traditional'),
        ('google', 'Google')
    ]
    
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    auth_method = models.CharField(max_length=20, choices=AUTH_METHOD_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
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
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Django auth fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = None
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username

    @property
    def is_online(self):
        """Check if user is currently online (active within last 5 minutes)"""
        if not self.last_activity:
            return False
        return (now() - self.last_activity).seconds < 300