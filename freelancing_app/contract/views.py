from .models import Contract, Transaction, Review, Workspace, TaskSubmission
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
from django.http import JsonResponse
from decimal import Decimal

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
        
        # Redirect to workspace if both parties have signed
        if contract.client_signature and contract.freelancer_signature:
            return redirect('contract:workspace', contract_id=contract_id)
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/client/contract-detail.html', context)

class FreelancerContractDetailView(BaseContractView):
    """View for freelancers to see the details of a contract."""
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:freelancer_contract_list')
        
        # Redirect to workspace if both parties have signed
        if contract.client_signature and contract.freelancer_signature:
            return redirect('contract:workspace', contract_id=contract_id)
        
        context = {
            'contract': contract,
            'active_tab': 'contracts'
        }
        return render(request, 'contract/freelancer/contract-details.html', context)

class WorkspaceView(BaseContractView):
    """View for managing workspace and submissions"""
    TEMPLATE_NAME = 'contract/workspace.html'
    
    def get(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, "Contract not found or you don't have permission to access it.")
            return redirect('contract:client_contract_list' if request.user.role == 'client' else 'contract:freelancer_contract_list')
            
        # Create workspace if it doesn't exist and both parties have signed
        if not hasattr(contract, 'workspace') and contract.client_signature and contract.freelancer_signature:
            workspace = Workspace.objects.create(contract=contract)
        else:
            workspace = getattr(contract, 'workspace', None)
            
        if not workspace:
            messages.warning(request, "Both parties must sign the contract before accessing the workspace.")
            return redirect('contract:client_contract_detail' if request.user.role == 'client' else 'contract:freelancer_contract_detail', contract_id=contract_id)
            
        submissions = workspace.submissions.all()
        
        # Get reviews for both client and freelancer
        client_review = contract.reviews.filter(reviewer_type=Review.ReviewerType.CLIENT).first()
        freelancer_review = contract.reviews.filter(reviewer_type=Review.ReviewerType.FREELANCER).first()
        
        context = {
            'contract': contract,
            'workspace': workspace,
            'submissions': submissions,
            'client_review': client_review,
            'freelancer_review': freelancer_review,
            'active_tab': 'workspace'
        }
        return render(request, self.TEMPLATE_NAME, context)

class CreateSubmissionView(BaseContractView):
    """View for creating new submissions"""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Only freelancers can create submissions.")
            return redirect('contract:freelancer_contract_list')
            
        workspace = getattr(contract, 'workspace', None)
        if not workspace:
            messages.error(request, "Workspace not found.")
            return redirect('contract:freelancer_contract_detail', contract_id=contract_id)
            
        description = request.POST.get('description', '').strip()
        attachment = request.FILES.get('attachment')
        
        if not description or not attachment:
            messages.error(request, "Please provide both description and attachment.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        # Handle attachment storage
        attachment_path = None
        if attachment:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'task_attachments'))
            filename = fs.save(attachment.name, attachment)
            attachment_path = 'task_attachments/' + os.path.basename(filename)
            
        submission = TaskSubmission.objects.create(
            workspace=workspace,
            description=description,
            attachment=attachment_path
        )
        
        # Notify client
        client_user = contract.proposal.project.client.user
        NotificationManager.send_notification(
            user=client_user,
            message=f"New work has been submitted for {contract.proposal.project.title}",
            redirect_url=reverse('contract:workspace', args=[contract.id])
        )
        
        messages.success(request, "Work submitted successfully for review.")
        return redirect('contract:workspace', contract_id=contract_id)

class ReviewSubmissionView(BaseContractView):
    """View for reviewing submitted work"""
    
    def post(self, request, contract_id, submission_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Only clients can review work.")
            return redirect('contract:client_contract_list')
            
        workspace = getattr(contract, 'workspace', None)
        if not workspace:
            messages.error(request, "Workspace not found.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
            
        submission = get_object_or_404(TaskSubmission, id=submission_id, workspace=workspace)
        
        if submission.status != 'submitted':
            messages.error(request, "This submission is not ready for review.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        action = request.POST.get('action', '').lower().strip()
        feedback = request.POST.get('feedback', '').strip()
        
        if not action:
            messages.error(request, "No action specified. Please select either Approve or Request Changes.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        if action == 'approve':
            submission.status = 'approved'
            message = "Work approved successfully."
        elif action == 'reject':
            submission.status = 'rejected'
            message = "Work rejected."
        else:
            messages.error(request, f"Invalid action: {action}. Please select either Approve or Request Changes.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        submission.feedback = feedback
        submission.save()
        
        # Notify freelancer
        freelancer_user = contract.proposal.freelancer.user
        NotificationManager.send_notification(
            user=freelancer_user,
            message=f"Your submission has been {action}d",
            redirect_url=reverse('contract:workspace', args=[contract.id])
        )
        
        messages.success(request, message)
        return redirect('contract:workspace', contract_id=contract_id)

class SubmitFinalWorkView(BaseContractView):
    """View for freelancers to submit final work"""
    
    def post(self, request, contract_id, submission_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'freelancer':
            messages.error(request, "Only freelancers can submit final work.")
            return redirect('contract:freelancer_contract_list')
            
        submission = get_object_or_404(TaskSubmission, id=submission_id, workspace=contract.workspace)
        
        if submission.status != 'approved':
            messages.error(request, "This submission is not approved for final work.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        final_description = request.POST.get('final_description', '').strip()
        final_attachment = request.FILES.get('final_attachment')
        
        if not final_description or not final_attachment:
            messages.error(request, "Please provide both a description and attachment for final work.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        submission.final_description = final_description
        submission.final_attachment = final_attachment
        submission.status = 'final_submitted'
        submission.save()
        
        # Notify client
        client_user = contract.proposal.project.client.user
        NotificationManager.send_notification(
            user=client_user,
            message=f"Final work has been submitted for {contract.proposal.project.title}",
            redirect_url=reverse('contract:workspace', args=[contract.id])
        )
        
        messages.success(request, "Final work submitted successfully.")
        return redirect('contract:workspace', contract_id=contract_id)
    
class ProcessPaymentView(BaseContractView):
    """View for processing contract payment"""
    
    def generate_esewa_signature(self, total_amount, transaction_uuid):
        """Generate signature for eSewa payment"""
        import hashlib
        import hmac
        import base64
        
        # Test credentials for college project
        secret_key = "8gBm/:&EnhH.1/q"
        product_code = "EPAYTEST"
        
        # Create the message string in the format required by eSewa
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        
        print("Debug - Message:", message)  # Debug print
        
        # Create HMAC SHA-256 hash
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Convert to base64
        signature = base64.b64encode(signature).decode('utf-8')
        
        print("Debug - Signature:", signature)  # Debug print
        
        return signature

    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract or request.user.role != 'client':
            messages.error(request, "Only clients can process payments.")
            return redirect('contract:client_contract_list')
            
        if contract.status != Contract.Status.ACTIVE:
            messages.error(request, "Only active contracts can be paid.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
            
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect('contract:client_contract_detail', contract_id=contract_id)
            
        # Create or update transaction
        transaction, created = Transaction.objects.get_or_create(
            contract=contract,
            defaults={
                'amount': contract.agreed_amount,
                'payment_method': payment_method,
                'status': Transaction.Status.PENDING
            }
        )
        
        if not created:
            transaction.payment_method = payment_method
            transaction.status = Transaction.Status.PENDING
            transaction.save()

        if payment_method == 'esewa':
            # For testing purposes, limit the amount to 1000
            test_amount = min(contract.agreed_amount, Decimal('1000.00'))
            
            # Calculate tax amount (assuming 13% VAT)
            tax_amount = (test_amount * Decimal('0.13')).quantize(Decimal('0.01'))
            total_amount = test_amount + tax_amount
            
            # Generate a unique transaction UUID
            transaction_uuid = f"TRX{transaction.id}{int(datetime.now().timestamp())}"
            
            # Update transaction with UUID
            transaction.transaction_uuid = transaction_uuid
            transaction.save()
            
            # Convert amounts to string with 2 decimal places
            amount_str = f"{float(test_amount):.2f}"
            tax_amount_str = f"{float(tax_amount):.2f}"
            total_amount_str = f"{float(total_amount):.2f}"
            
            # Prepare eSewa form data
            esewa_data = {
                'amount': amount_str,
                'tax_amount': tax_amount_str,
                'total_amount': total_amount_str,
                'transaction_uuid': transaction_uuid,
                'product_code': 'EPAYTEST',
                'product_service_charge': '0.00',
                'product_delivery_charge': '0.00',
                'success_url': request.build_absolute_uri(reverse('contract:payment_success')),
                'failure_url': request.build_absolute_uri(reverse('contract:payment_failure')),
                'signed_field_names': 'total_amount,transaction_uuid,product_code',
                'signature': self.generate_esewa_signature(total_amount_str, transaction_uuid)
            }
            
            print("Debug - Full eSewa Data:", esewa_data)  # Debug print
            
            # Return JSON response with form data
            return JsonResponse({
                'status': 'success',
                'redirect_url': 'https://rc-epay.esewa.com.np/api/epay/main/v2/form',
                'form_data': esewa_data
            })
            
        # For other payment methods, continue with existing logic
        transaction.status = Transaction.Status.COMPLETED
        transaction.save()
        
        # Update contract status
        contract.status = Contract.Status.COMPLETED
        contract.completed_date = datetime.now().date()
        contract.save()
        
        # Update project status
        project = contract.proposal.project
        project.status = 'completed'
        project.save()
        
        # Notify freelancer
        freelancer_user = contract.proposal.freelancer.user
        NotificationManager.send_notification(
            user=freelancer_user,
            message=f"Payment for {contract.proposal.project.title} has been processed",
            redirect_url=reverse('contract:freelancer_contract_detail', args=[contract.id])
        )
        
        # Notify client
        client_user = contract.proposal.project.client.user
        NotificationManager.send_notification(
            user=client_user,
            message=f"Project {contract.proposal.project.title} has been completed",
            redirect_url=reverse('contract:client_contract_detail', args=[contract.id])
        )
        
        messages.success(request, "Payment processed successfully and project marked as completed.")
        return redirect('contract:client_contract_detail', contract_id=contract_id)

class PaymentSuccessView(BaseContractView):
    """View for handling successful eSewa payments"""
    
    def get(self, request):
        # Get data from eSewa callback
        data = request.GET.get('data')
        if not data:
            messages.error(request, "Invalid payment response.")
            return redirect('home:home')
            
        try:
            import json
            import base64
            
            # Decode the base64 data
            decoded_data = base64.b64decode(data).decode('utf-8')
            payment_data = json.loads(decoded_data)
            
            print("Debug - Payment Data:", payment_data)  # Debug print
            
            # Get transaction details
            transaction_uuid = payment_data.get('transaction_uuid')
            status = payment_data.get('status')
            
            if not transaction_uuid or status != 'COMPLETE':
                messages.error(request, "Payment was not completed successfully.")
                return redirect('home:home')
                
            # Find the transaction
            transaction = Transaction.objects.get(transaction_uuid=transaction_uuid)
            contract = transaction.contract
            
            # Update transaction status
            transaction.status = Transaction.Status.COMPLETED
            transaction.save()
            
            # Update contract status
            contract.status = Contract.Status.COMPLETED
            contract.completed_date = datetime.now().date()
            contract.save()
            
            # Update project status
            project = contract.proposal.project
            project.status = 'completed'
            project.save()
            
            # Notify freelancer
            freelancer_user = contract.proposal.freelancer.user
            NotificationManager.send_notification(
                user=freelancer_user,
                message=f"Payment for {contract.proposal.project.title} has been processed",
                redirect_url=reverse('contract:freelancer_contract_detail', args=[contract.id])
            )
            
            # Notify client
            client_user = contract.proposal.project.client.user
            NotificationManager.send_notification(
                user=client_user,
                message=f"Project {contract.proposal.project.title} has been completed",
                redirect_url=reverse('contract:client_contract_detail', args=[contract.id])
            )
            
            messages.success(request, "Payment processed successfully and project marked as completed.")
            return redirect('contract:workspace', contract_id=contract.id)
            
        except (Transaction.DoesNotExist, json.JSONDecodeError, base64.binascii.Error) as e:
            print("Debug - Error:", str(e))  # Debug print
            messages.error(request, "Error processing payment response.")
            return redirect('home:home')

class PaymentFailureView(BaseContractView):
    """View for handling failed eSewa payments"""
    
    def get(self, request):
        # Get data from eSewa callback
        data = request.GET.get('data')
        if not data:
            messages.error(request, "Invalid payment response.")
            return redirect('home:home')
            
        try:
            import json
            import base64
            
            # Decode the base64 data
            decoded_data = base64.b64decode(data).decode('utf-8')
            payment_data = json.loads(decoded_data)
            
            print("Debug - Payment Data:", payment_data)  # Debug print
            
            # Get transaction details
            transaction_uuid = payment_data.get('transaction_uuid')
            
            if not transaction_uuid:
                messages.error(request, "Invalid payment response.")
                return redirect('home:home')
                
            # Find the transaction
            transaction = Transaction.objects.get(transaction_uuid=transaction_uuid)
            contract = transaction.contract
            
            # Update transaction status
            transaction.status = Transaction.Status.FAILED
            transaction.save()
            
            messages.error(request, "Payment processing failed. Please try again.")
            return redirect('contract:workspace', contract_id=contract.id)
            
        except (Transaction.DoesNotExist, json.JSONDecodeError, base64.binascii.Error) as e:
            print("Debug - Error:", str(e))  # Debug print
            messages.error(request, "Error processing payment response.")
            return redirect('home:home')

class LeaveReviewView(BaseContractView):
    """View for leaving reviews after work completion"""
    
    def post(self, request, contract_id):
        contract = self.get_contract(request, contract_id)
        if not contract:
            messages.error(request, "Contract not found.")
            return redirect('contract:client_contract_list' if request.user.role == 'client' else 'contract:freelancer_contract_list')
            
        # Check if user has already left a review
        existing_review = Review.objects.filter(
            contract=contract,
            reviewer_type=Review.ReviewerType.CLIENT if request.user.role == 'client' else Review.ReviewerType.FREELANCER
        ).first()
        
        if existing_review:
            messages.info(request, "You've already left a review for this contract.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text', '').strip()
        
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            messages.error(request, "Please provide a valid rating between 1 and 5.")
            return redirect('contract:workspace', contract_id=contract_id)
            
        review = Review.objects.create(
            contract=contract,
            reviewer_type=Review.ReviewerType.CLIENT if request.user.role == 'client' else Review.ReviewerType.FREELANCER,
            rating=rating,
            feedback=review_text
        )
        
        # Notify the other party
        other_user = contract.proposal.freelancer.user if request.user.role == 'client' else contract.proposal.project.client.user
        NotificationManager.send_notification(
            user=other_user,
            message=f"You've received a {rating}-star review for {contract.proposal.project.title}",
            redirect_url=reverse('contract:workspace', args=[contract.id])
        )
        
        messages.success(request, "Review submitted successfully.")
        return redirect('contract:workspace', contract_id=contract_id)