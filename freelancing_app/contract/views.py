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

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseContractView(CustomLoginRequiredMixin, View):
    """Base class for contract-related views with common functionality."""
    
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

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class CreateContractView(BaseContractView):
    """Handles creation of contracts from accepted proposals."""
    
    def post(self, request, proposal_id):
        try:
            proposal = get_object_or_404(
                Proposal,
                id=proposal_id,
                status='accepted',
                project__client__user=request.user
            )
            
            if hasattr(proposal, 'contract'):
                messages.warning(request, 'A contract already exists for this proposal.')
                return redirect('project:client-project-detail', project_id=proposal.project.id)
            
            agreed_amount = request.POST.get('agreed_amount')
            start_date = request.POST.get('start_date')
            duration_weeks = int(request.POST.get('duration_weeks', 4))
            terms = request.POST.get('terms', 'Standard platform terms apply.')
            
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = start_date + timedelta(weeks=duration_weeks)
            
            with transaction.atomic():
                contract = Contract.objects.create(
                    proposal=proposal,
                    agreed_amount=agreed_amount,
                    start_date=start_date,
                    end_date=end_date,
                    terms=terms,
                    client_signature=True  
                )
                
                if proposal.project.status != 'in_progress':
                    proposal.project.status = 'in_progress'
                    proposal.project.save()
                
                NotificationManager.send_notification(
                    user=proposal.freelancer.user,
                    message=f"New contract created for project {proposal.project.title[:30]}...",
                    redirect_url=reverse('contract:freelancer-contract-detail', kwargs={'contract_id': contract.id})
                )
                
            messages.success(request, 'Contract created successfully!')
            return redirect('contract:client-contract-detail', contract_id=contract.id)
            
        except Exception as e:
            print(f"[CreateContractView Error]: {e}")
            messages.error(request, 'Failed to create contract. Please try again.')
            return redirect('project:client-project-detail', project_id=proposal.project.id)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ClientContractDetailView(BaseContractView):
    """Detailed view of a contract for clients."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, 'Contract not found or access denied.')
            return redirect('project:client-projects')
            
        context = {
            'contract': contract,
            'work_submissions': contract.work_submissions.all().order_by('-submitted_at'),
            'can_approve': contract.status == Contract.Status.ACTIVE,
            'can_pay': not hasattr(contract, 'transaction') and contract.status == Contract.Status.ACTIVE,
            'can_review': contract.status == Contract.Status.COMPLETED and not hasattr(contract, 'review'),
        }
        return render(request, 'contract/client_contract_detail.html', context)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class FreelancerContractDetailView(BaseContractView):
    """Detailed view of a contract for freelancers."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, 'Contract not found or access denied.')
            return redirect('freelancer:dashboard')
            
        # Check if freelancer needs to sign
        needs_signature = not contract.freelancer_signature
        
        context = {
            'contract': contract,
            'work_submissions': contract.work_submissions.all().order_by('-submitted_at'),
            'needs_signature': needs_signature,
            'can_submit_work': contract.status == Contract.Status.ACTIVE and contract.freelancer_signature,
        }
        return render(request, 'contract/freelancer_contract_detail.html', context)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class SignContractView(BaseContractView):
    """Handles contract signing by freelancer."""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, 'Contract not found or access denied.')
            return redirect('freelancer:dashboard')
            
        if request.user.role != 'freelancer':
            messages.error(request, 'Only freelancers can sign contracts.')
            return redirect('freelancer:dashboard')
            
        if contract.freelancer_signature:
            messages.warning(request, 'You have already signed this contract.')
            return redirect('contract:freelancer-contract-detail', contract_id=contract.id)
            
        # Validate terms acceptance
        if request.POST.get('accept_terms') != 'on':
            messages.error(request, 'You must accept the terms to sign the contract.')
            return redirect('contract:freelancer-contract-detail', contract_id=contract.id)
            
        # Sign the contract
        contract.freelancer_signature = True
        contract.is_terms_accepted = True
        contract.save()
        
        # Send notification to client
        NotificationManager.send_notification(
            user=contract.proposal.project.client.user,
            message=f"Contract for project {contract.proposal.project.title[:30]}... has been signed by the freelancer.",
            redirect_url=reverse('contract:client-contract-detail', kwargs={'contract_id': contract.id})
        )
        
        messages.success(request, 'Contract signed successfully!')
        return redirect('contract:freelancer-contract-detail', contract_id=contract.id)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class SubmitWorkView(BaseContractView):
    """Handles work submissions by freelancers."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, 'Access denied.')
            return redirect('freelancer:dashboard')
            
        if not contract.freelancer_signature:
            messages.error(request, 'You must sign the contract before submitting work.')
            return redirect('contract:freelancer-contract-detail', contract_id=contract.id)
            
        return render(request, 'contract/submit_work.html', {'contract': contract})
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, 'Access denied.')
            return redirect('freelancer:dashboard')
            
        try:
            description = request.POST.get('description', '').strip()
            attachment = request.FILES.get('attachment')
            
            if not description and not attachment:
                messages.error(request, 'Either description or attachment is required.')
                return redirect('contract:submit-work', contract_id=contract.id)
                
            # Save the work submission
            submission = WorkSubmission(
                contract=contract,
                description=description,
                status=WorkSubmission.Status.PENDING
            )
            
            if attachment:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'work_submissions'))
                filename = fs.save(attachment.name, attachment)
                submission.attachment.name = os.path.join('work_submissions', filename)
                
            submission.save()
            
            # Send notification to client
            NotificationManager.send_notification(
                user=contract.proposal.project.client.user,
                message=f"New work submitted for project {contract.proposal.project.title[:30]}...",
                redirect_url=reverse('contract:client-contract-detail', kwargs={'contract_id': contract.id})
            )
            
            messages.success(request, 'Work submitted successfully!')
            return redirect('contract:freelancer-contract-detail', contract_id=contract.id)
            
        except Exception as e:
            print(f"[SubmitWorkView Error]: {e}")
            messages.error(request, 'Failed to submit work. Please try again.')
            return redirect('contract:submit-work', contract_id=contract.id)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ReviewWorkView(BaseContractView):
    """Handles work submission reviews by clients."""
    
    def post(self, request, submission_id, action):
        try:
            submission = get_object_or_404(
                WorkSubmission,
                id=submission_id,
                contract__proposal__project__client__user=request.user
            )
            
            if action == 'approve':
                submission.status = WorkSubmission.Status.APPROVED
                messages.success(request, 'Work approved successfully!')
                
                # Check if this was the final deliverable
                if request.POST.get('mark_complete') == 'on':
                    submission.contract.status = Contract.Status.COMPLETED
                    submission.contract.completed_date = datetime.now().date()
                    submission.contract.save()
                    
                    # Send notification to freelancer
                    NotificationManager.send_notification(
                        user=submission.contract.proposal.freelancer.user,
                        message=f"Your work for project {submission.contract.proposal.project.title[:30]}... has been approved and marked complete!",
                        redirect_url=reverse('contract:freelancer-contract-detail', kwargs={'contract_id': submission.contract.id})
                    )
                    
            elif action == 'reject':
                submission.status = WorkSubmission.Status.REJECTED
                rejection_reason = request.POST.get('rejection_reason', '')
                submission.description = f"[REJECTED - {rejection_reason}]\n\n{submission.description}"
                messages.warning(request, 'Work rejected.')
                
                # Send notification to freelancer
                NotificationManager.send_notification(
                    user=submission.contract.proposal.freelancer.user,
                    message=f"Your work for project {submission.contract.proposal.project.title[:30]}... needs revision: {rejection_reason}",
                    redirect_url=reverse('contract:freelancer-contract-detail', kwargs={'contract_id': submission.contract.id})
                )
                
            submission.save()
            return redirect('contract:client-contract-detail', contract_id=submission.contract.id)
            
        except Exception as e:
            print(f"[ReviewWorkView Error]: {e}")
            messages.error(request, 'Failed to process your request.')
            return redirect('project:client-projects')

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProcessPaymentView(BaseContractView):
    """Handles payment processing by clients."""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, 'Access denied.')
            return redirect('project:client-projects')
            
        try:
            # Validate no existing transaction
            if hasattr(contract, 'transaction'):
                messages.warning(request, 'Payment already processed for this contract.')
                return redirect('contract:client-contract-detail', contract_id=contract.id)
                
            payment_method = request.POST.get('payment_method')
            
            # Create transaction (in a real app, this would integrate with a payment gateway)
            transaction = Transaction.objects.create(
                contract=contract,
                amount=contract.agreed_amount,
                payment_method=payment_method,
                status=Transaction.Status.COMPLETED
            )
            
            # Send notification to freelancer
            NotificationManager.send_notification(
                user=contract.proposal.freelancer.user,
                message=f"Payment received for project {contract.proposal.project.title[:30]}...",
                redirect_url=reverse('contract:freelancer-contract-detail', kwargs={'contract_id': contract.id})
            )
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('contract:client-contract-detail', contract_id=contract.id)
            
        except Exception as e:
            print(f"[ProcessPaymentView Error]: {e}")
            messages.error(request, 'Failed to process payment. Please try again.')
            return redirect('contract:client-contract-detail', contract_id=contract.id)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: 
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class SubmitReviewView(BaseContractView):
    """Handles submission of reviews by clients."""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, 'Access denied.')
            return redirect('project:client-projects')
            
        try:
            rating = int(request.POST.get('rating'))
            feedback = request.POST.get('feedback', '').strip()
            
            # Validate rating
            if rating < 1 or rating > 5:
                messages.error(request, 'Invalid rating value.')
                return redirect('contract:client-contract-detail', contract_id=contract.id)
                
            # Create review
            Review.objects.create(
                contract=contract,
                rating=rating,
                feedback=feedback
            )
            
            # Send notification to freelancer
            NotificationManager.send_notification(
                user=contract.proposal.freelancer.user,
                message=f"You received a {rating}★ review for project {contract.proposal.project.title[:30]}...",
                redirect_url=reverse('contract:freelancer-contract-detail', kwargs={'contract_id': contract.id})
            )
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('contract:client-contract-detail', contract_id=contract.id)
            
        except Exception as e:
            print(f"[SubmitReviewView Error]: {e}")
            messages.error(request, 'Failed to submit review. Please try again.')
            return redirect('contract:client-contract-detail', contract_id=contract.id)