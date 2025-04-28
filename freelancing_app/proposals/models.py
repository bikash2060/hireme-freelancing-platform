from django.db import models
from freelancerprofile.models import Freelancer
from projects.models import Project

class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', ('Pending')
        ACCEPTED = 'accepted', ('Accepted')
        REJECTED = 'rejected', ('Rejected')
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='proposals')
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in weeks")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_shortlisted = models.BooleanField(default=False)
    
    available_start_date = models.DateField(null=True, blank=True)
    approach_methodology = models.TextField(blank=True)
    relevant_experience = models.TextField(blank=True)
    questions_for_client = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['project', 'freelancer']
        db_table = "proposal"

    def __str__(self):
        return f"Proposal for {self.project.title} by {self.freelancer.username}"


class ProposalAttachment(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='proposal_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.proposal.project.title}"
    
    class Meta:
        db_table = "proposal_attachment"
