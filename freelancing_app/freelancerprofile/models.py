from django.db import models
from accounts.models import Freelancer

class Education(models.Model):
    id = models.AutoField(primary_key=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name="educations")
    education_level = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='education_logos/', null=True, blank=True)

    def __str__(self):
        return f"{self.education_level} at {self.institution} ({self.freelancer.user.username})"

    class Meta:
        db_table = "education"

class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name="certificates")
    certificate_name = models.CharField(max_length=255)
    certificate_provider = models.CharField(max_length=255)
    issued_date = models.DateField(null=True, blank=True)
    certificate_logo = models.ImageField(upload_to='certificate_logos/', null=True, blank=True)
    certificate_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.certificate_name} - {self.freelancer.user.username}"

    class Meta:
        db_table = "certificate"