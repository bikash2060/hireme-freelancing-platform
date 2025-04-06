from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now, timedelta
from django.db import models

def default_expired_time():
    return now() + timedelta(minutes=3)

class Country(models.Model):
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
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
        unique_together = ('name', 'country') 
        db_table = 'city'
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    
class OTPCode(models.Model):
    id = models.AutoField(primary_key=True)
    otp_code = models.CharField(max_length=6)
    email = models.EmailField()
    otp_generated_time = models.DateTimeField(default=now)
    otp_expired_time = models.DateTimeField(default=default_expired_time)
    is_verified = models.BooleanField(default=False)  

    class Meta:
        db_table = "OTPCode"

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=200)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=[
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
        ('admin', 'Admin')
    ])
    auth_method = models.CharField(max_length=20, choices=[
        ('traditional', 'Traditional'),
        ('google', 'Google')
    ])
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False) 
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  
    bio = models.TextField(blank=True, null=True)  
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    
    last_login = None
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"

