from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from notification.utils import NotificationManager
from .models import Proposal, ProposalAttachment
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from projects.models import Project
from .utils import ProposalValidator
from django.views import View
from django.contrib import messages
from django.conf import settings
from freelancerprofile.models import Freelancer
import os

class SubmitProposalView(CustomLoginRequiredMixin, View):
    template_name = 'proposals/newproposal.html'
    project_detail_url = 'home:project-detail'
    
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            freelancer = Freelancer.objects.get(user=request.user)
            
            # Check if freelancer already submitted a proposal
            if Proposal.objects.filter(project=project, freelancer=freelancer).exists():
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(self.project_detail_url, project_id=project.id)
                
            return render(request, self.template_name, {
                'project': project,
                'freelancer': freelancer
            })
            
        except Freelancer.DoesNotExist:
            messages.error(request, 'Only freelancers can submit proposals.')
            return redirect(self.project_detail_url, project_id=project_id)
            
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect('home:projects')
    
    def post(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            freelancer = Freelancer.objects.get(user=request.user)
            
            # Check if freelancer already submitted a proposal
            if Proposal.objects.filter(project=project, freelancer=freelancer).exists():
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(self.project_detail_url, project_id=project.id)
            
            cover_letter = request.POST.get('cover_letter', '').strip()
            proposed_amount = request.POST.get('proposed_amount')
            estimated_duration = request.POST.get('estimated_duration')
            attachments = request.FILES.getlist('attachment[]')
            
            # Validate proposal data
            is_valid, error_message = ProposalValidator.validate_proposal_data(
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                attachments=attachments,
                project=project
            )
            
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.template_name, {
                    'project': project,
                    'freelancer': freelancer,
                    'cover_letter': cover_letter,
                    'proposed_amount': proposed_amount,
                    'estimated_duration': estimated_duration
                })
            
            # Create the proposal
            proposal = Proposal.objects.create(
                project=project,
                freelancer=freelancer,
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                status=Proposal.Status.PENDING
            )
            
            # Handle attachments
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'proposal_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProposalAttachment.objects.create(
                        proposal=proposal,
                        file=filename.split('/')[-1]
                    )
            
            # Send notification to client
            NotificationManager.send_notification(
                user=project.client.user,
                message=f"New proposal received for your project '{project.title}' from {freelancer.user.get_full_name()}",
                redirect_url=f"/projects/{project.id}/proposals/{proposal.id}/"
            )
            
            messages.success(request, 'Your proposal has been submitted successfully!')
            return redirect(self.project_detail_url, project_id=project.id)
            
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong while submitting your proposal.')
            return redirect(self.project_detail_url, project_id=project_id)