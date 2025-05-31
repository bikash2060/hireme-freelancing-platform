from django.utils.translation import gettext_lazy as _
from proposals.models import Proposal
from django.db import models

class Contract(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        DISPUTED = 'disputed', _('Disputed')

    proposal = models.OneToOneField(
        Proposal,
        on_delete=models.CASCADE,
        related_name='contract'
    )
    agreed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final negotiated amount"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client_signature = models.BooleanField(default=False)
    freelancer_signature = models.BooleanField(default=False)

    def __str__(self):
        return f"Contract #{self.id} - {self.proposal.project.title}"

    class Meta:
        db_table = "contract"
        ordering = ['-created_at']

class Workspace(models.Model):
    """Workspace for project collaboration between client and freelancer"""
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='workspace'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Workspace for {self.contract.proposal.project.title}"
    
    class Meta:
        db_table = "workspace"

class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('final_submitted', 'Final Work Submitted'),
        ('completed', 'Completed')
    ]
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='submissions')
    description = models.TextField()
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    feedback = models.TextField(blank=True)
    final_description = models.TextField(blank=True)
    final_attachment = models.FileField(upload_to='final_submissions/', blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Submission #{self.id} - {self.status}"

class Transaction(models.Model):
    class Status(models.TextChoices):   
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='transaction'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        help_text=_("E.g., Esewa, Khalti, Bank Transfer")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        db_table = "transaction"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Transaction for Contract #{self.contract.id}"
    
class Review(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],  
        help_text="Rating between 1 (worst) to 5 (best)"
    )
    feedback = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for Contract #{self.contract.id}"