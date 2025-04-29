from .models import Contract, WorkSubmission, Transaction, Review
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from notification.utils import NotificationManager
from freelancerprofile.models import Freelancer
from datetime import datetime, timedelta
from proposals.models import Proposal
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.views import View
import os

class BaseContractView(CustomLoginRequiredMixin, View):
    """Base class for contract-related views with common functionality."""
    
    HOME_URL = 'home:home'
    
    def get_contract(self, request, contract_id):
        """Get contract with validation for both client and freelancer."""
        try:
            if request.user.role == 'client':
                return Contract.objects.get(
                    id=contract_id,
                    proposal__project__client__user=request.user
                )
            elif request.user.role == 'freelancer':
                return Contract.objects.get(
                    id=contract_id,
                    proposal__freelancer__user=request.user
                )
            else:
                raise Contract.DoesNotExist
        except Contract.DoesNotExist:
            return None

class BaseContractListView(BaseContractView):
    """Base class for contract list views."""
    TEMPLATE_NAME = None
    ACTIVE_TAB = 'contracts'
    
    def get_queryset(self):
        raise NotImplementedError("Subclasses must implement get_queryset()")
    
    def get(self, request):
        if not self.has_permission(request):
            messages.error(request, "You don't have permission to view this page.")
            return redirect(self.HOME_URL)
            
        contracts = self.get_queryset()
        
        context = {
            'contracts': contracts,
            'active_tab': self.ACTIVE_TAB
        }
        return render(request, self.TEMPLATE_NAME, context)
    
    def has_permission(self, request):
        raise NotImplementedError("Subclasses must implement has_permission()")

class BaseSignContractView(BaseContractView):
    """Base class for signing contracts."""
    TEMPLATE_NAME = None
    SIGNATURE_FIELD = None
    REDIRECT_VIEW = None
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect(self.REDIRECT_VIEW)
            
        if getattr(contract, self.SIGNATURE_FIELD):
            messages.info(request, "You've already signed this contract.")
            return redirect(self.REDIRECT_VIEW)
            
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, self.TEMPLATE_NAME, context)
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect(self.REDIRECT_VIEW)
            
        if getattr(contract, self.SIGNATURE_FIELD):
            messages.info(request, "You've already signed this contract.")
            return redirect(self.REDIRECT_VIEW)
            
        # Mark contract as signed
        setattr(contract, self.SIGNATURE_FIELD, True)
        contract.save()
        
        messages.success(request, "Congratulations! You've successfully signed the contract.")
        return redirect(self.REDIRECT_VIEW)

class ClientContractListView(BaseContractListView):
    """View for clients to see all their contracts."""
    TEMPLATE_NAME = 'contract/client/contract-list.html'
    
    def get_queryset(self):
        return Contract.objects.filter(
            proposal__project__client__user=self.request.user
        ).select_related(
            'proposal__project',
            'proposal__freelancer__user'
        ).order_by('-created_at')
    
    def has_permission(self, request):
        return request.user.role == 'client'

class ClientSignContractView(BaseSignContractView):
    """View for clients to sign contracts."""
    TEMPLATE_NAME = 'contract/client/sign_contract.html'
    SIGNATURE_FIELD = 'client_signature'
    REDIRECT_VIEW = 'contract:client_contract_list'

class FreelancerContractListView(BaseContractListView):
    """View for freelancers to see all their contracts."""
    TEMPLATE_NAME = 'contract/freelancer/contract-list.html'
    
    def get_queryset(self):
        return Contract.objects.filter(
            proposal__freelancer__user=self.request.user
        ).select_related(
            'proposal__project',
            'proposal__project__client__user'
        ).order_by('-created_at')
    
    def has_permission(self, request):
        return request.user.role == 'freelancer'

class FreelancerSignContractView(BaseSignContractView):
    """View for freelancers to sign contracts."""
    TEMPLATE_NAME = 'contract/freelancer/sign_contract.html'
    SIGNATURE_FIELD = 'freelancer_signature'
    REDIRECT_VIEW = 'contract:freelancer_contract_list'

class ClientContractDetailView(BaseContractView):
    """View for clients to see the details of a contract."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:client_contract_list')
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/client/contract_detail.html', context)

class FreelancerContractDetailView(BaseContractView):
    """View for freelancers to see the details of a contract."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:freelancer_contract_list')
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/freelancer/contract_detail.html', context)

# Work Submission Views
class FreelancerSubmitWorkView(BaseContractView):
    """View for freelancers to submit work for a contract."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:freelancer_contract_list')
        
        if contract.status != Contract.Status.ACTIVE:
            messages.error(request, "You can only submit work for active contracts.")
            return redirect('contract:freelancer_contract_detail', contract_id=contract_id)
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/freelancer/submit_work.html', context)
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:freelancer_contract_list')
        
        if contract.status != Contract.Status.ACTIVE:
            messages.error(request, "You can only submit work for active contracts.")
            return redirect('contract:freelancer_contract_detail', contract_id=contract_id)
        
        description = request.POST.get('description', '')
        attachment = request.FILES.get('attachment')
        
        submission = WorkSubmission(
            contract=contract,
            description=description
        )
        
        if attachment:
            submission.attachment = attachment
        
        submission.save()
        
        # Notify client about new submission
        client_user = contract.proposal.project.client.user
        NotificationManager.create_notification(
            user=client_user,
            title="New Work Submission",
            message=f"Freelancer has submitted work for {contract.proposal.project.title}",
            link=reverse('contract:client_contract_detail', args=[contract.id])
        )
        
        messages.success(request, "Work submitted successfully.")
        return redirect('contract:freelancer_contract_detail', contract_id=contract_id)

class ClientReviewSubmissionView(BaseContractView):
    """View for clients to review work submissions."""
    
    def post(self, request, submission_id):
        try:
            submission = WorkSubmission.objects.select_related(
                'contract__proposal__project__client__user'
            ).get(id=submission_id)
            
            # Verify client owns this contract
            if request.user != submission.contract.proposal.project.client.user:
                messages.error(request, "You don't have permission to review this submission.")
                return redirect('contract:client_contract_list')
            
            action = request.POST.get('action')
            
            if action == 'approve':
                submission.status = WorkSubmission.Status.APPROVED
                submission.save()
                
                # Notify freelancer
                freelancer_user = submission.contract.proposal.freelancer.user
                NotificationManager.create_notification(
                    user=freelancer_user,
                    title="Work Submission Approved",
                    message=f"Your work submission for {submission.contract.proposal.project.title} has been approved",
                    link=reverse('contract:freelancer_contract_detail', args=[submission.contract.id])
                )
                
                messages.success(request, "Work submission approved.")
            
            elif action == 'reject':
                submission.status = WorkSubmission.Status.REJECTED
                submission.save()
                
                # Notify freelancer
                freelancer_user = submission.contract.proposal.freelancer.user
                NotificationManager.create_notification(
                    user=freelancer_user,
                    title="Work Submission Rejected",
                    message=f"Your work submission for {submission.contract.proposal.project.title} has been rejected",
                    link=reverse('contract:freelancer_contract_detail', args=[submission.contract.id])
                )
                
                messages.success(request, "Work submission rejected.")
            
            return redirect('contract:client_contract_detail', contract_id=submission.contract.id)
            
        except WorkSubmission.DoesNotExist:
            messages.error(request, "Submission not found.")
            return redirect('contract:client_contract_list')

# Contract Completion Views
class ClientCompleteContractView(BaseContractView):
    """View for clients to mark a contract as completed."""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:client_contract_list')
        
        if contract.status != Contract.Status.ACTIVE:
            messages.error(request, "Only active contracts can be marked as completed.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        # Check if there are any approved submissions
        if not contract.work_submissions.filter(status=WorkSubmission.Status.APPROVED).exists():
            messages.error(request, "There must be at least one approved work submission before completing the contract.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        with transaction.atomic():
            # Update contract status
            contract.status = Contract.Status.COMPLETED
            contract.completed_date = datetime.now().date()
            contract.save()
            
            # Create transaction record (if not exists)
            Transaction.objects.get_or_create(
                contract=contract,
                defaults={
                    'amount': contract.agreed_amount,
                    'payment_method': 'System',
                    'status': Transaction.Status.COMPLETED
                }
            )
            
            # Notify freelancer
            freelancer_user = contract.proposal.freelancer.user
            NotificationManager.create_notification(
                user=freelancer_user,
                title="Contract Completed",
                message=f"Contract for {contract.proposal.project.title} has been marked as completed",
                link=reverse('contract:freelancer_contract_detail', args=[contract.id])
            )
        
        messages.success(request, "Contract has been marked as completed successfully.")
        return redirect('contract:client_contract_detail', contract_id=contract_id)

# Review Views
class ClientLeaveReviewView(BaseContractView):
    """View for clients to leave reviews for completed contracts."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:client_contract_list')
        
        if contract.status != Contract.Status.COMPLETED:
            messages.error(request, "You can only leave reviews for completed contracts.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        # Check if review already exists
        if hasattr(contract, 'review'):
            messages.info(request, "You've already left a review for this contract.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/client/leave_review.html', context)
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:client_contract_list')
        
        if contract.status != Contract.Status.COMPLETED:
            messages.error(request, "You can only leave reviews for completed contracts.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        # Check if review already exists
        if hasattr(contract, 'review'):
            messages.info(request, "You've already left a review for this contract.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
        
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback', '')
        
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            messages.error(request, "Please provide a valid rating between 1 and 5.")
            return redirect('contract:client_leave_review', contract_id=contract_id)
        
        # Create review
        review = Review(
            contract=contract,
            rating=rating,
            feedback=feedback
        )
        review.save()
        
        # Notify freelancer
        freelancer_user = contract.proposal.freelancer.user
        NotificationManager.create_notification(
            user=freelancer_user,
            title="New Review Received",
            message=f"You've received a {rating}-star review for {contract.proposal.project.title}",
            link=reverse('contract:freelancer_contract_detail', args=[contract.id])
        )
        
        messages.success(request, "Review submitted successfully.")
        return redirect('contract:client_contract_detail', contract_id=contract_id)