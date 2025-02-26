from django.db import models
from accounts.models import Freelancer
from projects.models import Project

class Proposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')  
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='proposals')  
    proposal_description = models.TextField()  
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    posted_date = models.DateTimeField(auto_now_add=True)  
    estimated_delivery_time = models.DateField()  
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ], default='pending')  

    def __str__(self):
        return f"Proposal for {self.project.title} by {self.freelancer.user.username}"

    class Meta:
        db_table = 'proposal'