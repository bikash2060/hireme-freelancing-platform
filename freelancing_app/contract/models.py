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
        db_table = "task_submission"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Submission #{self.id} - {self.status}"

class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    class Meta:
        db_table = "transaction"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Transaction {self.id} - {self.contract.proposal.project.title}"

class Review(models.Model):
    class ReviewerType(models.TextChoices):
        CLIENT = 'client', _('Client')
        FREELANCER = 'freelancer', _('Freelancer')

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer_type = models.CharField(
        max_length=20,
        choices=ReviewerType.choices,
        help_text="Whether the review is from client or freelancer"
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
        unique_together = ['contract', 'reviewer_type']

    def __str__(self):
        return f"{self.reviewer_type.title()} Review for Contract #{self.contract.id}"

    @classmethod
    def get_freelancer_stats(cls, freelancer):
        """Calculate review statistics for a freelancer"""
        reviews = cls.objects.filter(
            contract__proposal__freelancer=freelancer,
            reviewer_type=cls.ReviewerType.CLIENT
        ).select_related(
            'contract__proposal__project__client__user'
        ).order_by('-created_at')
        
        total_reviews = reviews.count()
        if total_reviews == 0:
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)},
                'on_time_delivery': 0,
                'reviews': []
            }
            
        # Calculate average rating
        average_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        
        # Calculate rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[i] = count
            
        # Calculate on-time delivery percentage
        completed_contracts = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status=Contract.Status.COMPLETED
        )
        total_completed = completed_contracts.count()
        on_time_deliveries = completed_contracts.filter(
            completed_date__lte=models.F('end_date')
        ).count()
        
        on_time_delivery = (on_time_deliveries / total_completed * 100) if total_completed > 0 else 0
        
        return {
            'average_rating': round(average_rating, 1),
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution,
            'on_time_delivery': round(on_time_delivery, 1),
            'reviews': reviews[:10]  # Get the 10 most recent reviews
        }