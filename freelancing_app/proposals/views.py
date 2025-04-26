from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from notification.utils import NotificationManager
from .models import Proposal, ProposalAttachment
from freelancerprofile.models import Freelancer
from django.core.paginator import Paginator
from .utils import ProposalValidator
from django.contrib import messages
from projects.models import Project
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.views import View
import json
import os

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProposalView
# Description: Base class for proposal-related views with utility methods
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseProposalView(CustomLoginRequiredMixin, View):
    """
    Base class for proposal-related views. Provides utility methods and constants.
    Restricts access to users with the 'freelancer' role.
    """
    HOME_URL = 'home:home'
    PROJECTS_URL = 'home:projects'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user has freelancer role before proceeding.
        """
        
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        if not hasattr(request.user, 'role') or request.user.role != 'freelancer':
            messages.error(request, "Access denied. You must be a freelancer to view this page.")
            return redirect(self.HOME_URL)
        return super().dispatch(request, *args, **kwargs)
    
    def get_freelancer(self, request):
        """
        Get freelancer instance for the logged-in user.
        """
        return Freelancer.objects.get(user=request.user)

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: SubmitProposalView
# Description: Handles submission of new proposals
# Tested On: 
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class SubmitProposalView(BaseProposalView):
    """
    - Handles submission of new proposals
    - Manages proposal details, attachments, and notifications
    """
    TEMPLATE_NAME = 'proposals/newproposal.html'
    PROJECT_DETAIL_URL = 'home:project-detail'
    
    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            freelancer = self.get_freelancer(request)
            
            # Check if freelancer already submitted a proposal
            if Proposal.objects.filter(project=project, freelancer=freelancer).exists():
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(self.PROJECT_DETAIL_URL, project_id=project.id)
                
            return render(request, self.TEMPLATE_NAME, {
                'project': project,
                'freelancer': freelancer
            })
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect(self.PROJECTS_URL)
            
        except Exception as e:
            print(f"[SubmitProposalView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROJECTS_URL)
    
    def post(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            freelancer = self.get_freelancer(request)
            
            # Check if freelancer already submitted a proposal
            if Proposal.objects.filter(project=project, freelancer=freelancer).exists():
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(self.PROJECT_DETAIL_URL, project_id=project.id)
            
            # Get form data
            cover_letter = request.POST.get('cover_letter', '').strip()
            proposed_amount = request.POST.get('proposed_amount')
            estimated_duration = request.POST.get('estimated_duration')
            approach_methodology = request.POST.get('approach_methodology', '').strip()
            relevant_experience = request.POST.get('relevant_experience', '').strip()
            questions_for_client = request.POST.get('questions_for_client', '').strip()
            available_start_date = request.POST.get('available_start_date', '').strip()
            attachments = request.FILES.getlist('attachment[]')
            
            # Convert empty date to None
            if not available_start_date:
                available_start_date = None
            
            # Prepare context for form re-rendering
            context = {
                'project': project,
                'freelancer': freelancer,
                'cover_letter': cover_letter,
                'proposed_amount': proposed_amount,
                'estimated_duration': estimated_duration,
                'approach_methodology': approach_methodology,
                'relevant_experience': relevant_experience,
                'questions_for_client': questions_for_client,
                'available_start_date': available_start_date
            }
            
            # Validate proposal data
            is_valid, error_message = ProposalValidator.validate_proposal_data(
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                attachments=attachments,
                project=project,
                approach_methodology=approach_methodology,
                relevant_experience=relevant_experience,
                questions_for_client=questions_for_client,
                available_start_date=available_start_date
            )
            
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME, context)
            
            # Create the proposal
            proposal = Proposal.objects.create(
                project=project,
                freelancer=freelancer,
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                approach_methodology=approach_methodology,
                relevant_experience=relevant_experience,
                questions_for_client=questions_for_client,
                available_start_date=available_start_date,
                status=Proposal.Status.PENDING
            )
            
            # Handle attachments
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'proposal_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProposalAttachment.objects.create(
                        proposal=proposal,
                        file=os.path.basename(filename)
                    )
            
            # Send notification to client
            NotificationManager.send_notification(
                user=project.client.user,
                message=f"New proposal received for your project {project.title} from {freelancer.user.full_name}.",
                redirect_url=None
            )
            
            messages.success(request, 'Your proposal has been submitted successfully!')
            return redirect(self.HOME_URL)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect('home:projects')
            
        except Exception as e:
            print(f"[SubmitProposalView POST Error]: {e}")
            messages.error(request, 'Something went wrong while submitting your proposal.')
            return redirect(self.PROJECT_DETAIL_URL, project_id=project_id)

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: FreelancerProposalsView
# Description: Displays and filters freelancer's proposals
# Tested On: 
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class FreelancerProposalsView(BaseProposalView):
    """
    - Displays paginated list of freelancer's proposals
    - Provides filtering by status, project category, and budget
    - Includes search functionality
    """
    TEMPLATE_NAME = 'proposals/proposals.html'
    ITEMS_PER_PAGE = 10

    def get(self, request):
        try:           
            freelancer = self.get_freelancer(request)
            proposals_list = Proposal.objects.filter(freelancer=freelancer).order_by('-created_at')
            
            # Get filter values from request
            selected_statuses = request.GET.getlist('status')
            selected_categories = request.GET.getlist('category')
            selected_budgets = request.GET.getlist('budget')
            keyword = request.GET.get('search')
            
            # Search by keyword
            if keyword:
                proposals_list = proposals_list.filter(
                    Q(project__title__icontains=keyword) |
                    Q(status__icontains=keyword) |
                    Q(project__category__name__icontains=keyword)
                )
                
            # Filter by status
            if selected_statuses and 'all' not in selected_statuses:
                proposals_list = proposals_list.filter(status__in=selected_statuses)
                
            # Filter by project category
            if selected_categories and 'all' not in selected_categories:
                proposals_list = proposals_list.filter(project__category_id__in=selected_categories)
                
            # Filter by budget
            if selected_budgets and 'all' not in selected_budgets:
                budget_q = Q()
                for b in selected_budgets:
                    if b == '500000+':
                        budget_q |= Q(proposed_amount__gte=500000)
                    else:
                        parts = b.split('-')
                        if len(parts) == 2:
                            min_val, max_val = map(int, parts)
                            budget_q |= Q(proposed_amount__gte=min_val, proposed_amount__lte=max_val)
                proposals_list = proposals_list.filter(budget_q)
                
            # Pagination
            paginator = Paginator(proposals_list, self.ITEMS_PER_PAGE)
            page_number = request.GET.get('page')
            proposals = paginator.get_page(page_number)
            
            # Get categories for filter options
            from projects.models import ProjectCategory
            categories = ProjectCategory.objects.all().order_by('name')
            
            context = {
                'proposals': proposals,
                'status_choices': Proposal.Status.choices,
                'categories': categories,
                'selected_statuses': selected_statuses,
                'selected_categories': selected_categories,
                'selected_budgets': selected_budgets,
                'search_keyword': keyword,
                'categories_dict': {str(c.id): c for c in categories},
            }
            return render(request, self.TEMPLATE_NAME, context)
            
        except Exception as e:
            print(f"[FreelancerProposalsView Error]: {e}")
            messages.error(request, 'Something went wrong while loading your proposals.')
            return redirect(self.HOME_URL)

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: FreelancerProposalDetailView
# Description: Displays detailed view of a freelancer's proposal
# Tested On:
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class FreelancerProposalDetailView(BaseProposalView):
    """
    - Shows detailed view of a freelancer's proposal
    - Includes proposal info, attachments, and management options
    """
    TEMPLATE_NAME = 'proposals/proposal-detail.html'
    PROPOSALS_URL = 'proposal:freelancer-proposals'

    def get(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.prefetch_related(
                'proposal_attachments'
            ).get(id=proposal_id, freelancer=freelancer)
            
            # Get project details
            project = proposal.project
            
            # Prepare attachments
            attachments = []
            for attachment in proposal.proposal_attachments.all():
                try:
                    if os.path.exists(attachment.file.path):
                        attachments.append({
                            'file': attachment.file,
                            'filename': os.path.basename(attachment.file.name),
                            'uploaded_at': attachment.uploaded_at
                        })
                    else:
                        filename = os.path.basename(attachment.file.name)
                        proposal_attachments_path = os.path.join(settings.MEDIA_ROOT, 'proposal_attachments', filename)
                        if os.path.exists(proposal_attachments_path):
                            attachment.file.name = filename
                            attachment.save()
                            attachments.append({
                                'file': attachment.file,
                                'filename': filename,
                                'uploaded_at': attachment.uploaded_at
                            })
                except Exception as e:
                    print(f"[Attachment Error]: {e}")
                    continue
                    
            context = {
                'proposal': proposal,
                'project': project,
                'freelancer': freelancer,
                'attachments': attachments,
            }
            
            return render(request, self.TEMPLATE_NAME, context)
            
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to view it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[FreelancerProposalDetailView Error]: {e}")
            messages.error(request, 'Something went wrong while loading the proposal.')
            return redirect(self.PROPOSALS_URL)

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: EditProposalView
# Description: Handles editing of existing proposals
# Tested On:
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class EditProposalView(BaseProposalView):
    """
    - Handles editing of existing proposals
    - Uses similar logic to SubmitProposalView but with existing proposal data
    - Prevents editing of non-pending proposals
    """
    TEMPLATE_NAME = 'proposals/editproposal.html'
    PROPOSAL_URL = 'proposal:freelancer-proposal-detail'
    PROPOSALS_URL = 'proposal:freelancer-proposals'

    def get(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.prefetch_related(
                'proposal_attachments'
            ).get(id=proposal_id, freelancer=freelancer)
            
            # Don't allow editing of non-pending proposals
            if proposal.status != Proposal.Status.PENDING:
                messages.error(request, 'Only pending proposals can be edited.')
                return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))
            
            # Prepare existing attachments
            existing_attachments = []
            if proposal.proposal_attachments.all():
                for attachment in proposal.proposal_attachments.all():
                    try:
                        file_path = os.path.join(settings.MEDIA_ROOT, str(attachment.file))
                        if os.path.exists(file_path):
                            attachment_data = {
                                'id': attachment.id,
                                'name': os.path.basename(attachment.file.name),
                                'url': attachment.file.url,
                                'size': os.path.getsize(file_path),
                                'uploaded_at': attachment.uploaded_at.isoformat() if attachment.uploaded_at else None
                            }
                            existing_attachments.append(attachment_data)
                        else:
                            print(f"[Attachment Warning]: File not found at {file_path}")
                    except Exception as e:
                        print(f"[Attachment Error]: {e}")
                        continue
            
            context = {
                'proposal': proposal,
                'project': proposal.project,
                'freelancer': freelancer,
                'existing_attachments_json': json.dumps(existing_attachments),
            }
            
            return render(request, self.TEMPLATE_NAME, context)
            
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to edit it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[EditProposalView GET Error]: {e}")
            messages.error(request, 'Something went wrong while loading the proposal for editing.')
            return redirect(self.PROPOSALS_URL)

    def post(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.get(id=proposal_id, freelancer=freelancer)
            
            # Don't allow editing of non-pending proposals
            if proposal.status != Proposal.Status.PENDING:
                messages.error(request, 'Only pending proposals can be edited.')
                return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))
            
            # Get form data
            cover_letter = request.POST.get('cover_letter', '').strip()
            proposed_amount = request.POST.get('proposed_amount')
            estimated_duration = request.POST.get('estimated_duration')
            attachments = request.FILES.getlist('attachment[]')
            
            # Prepare context for form re-rendering
            context = {
                'proposal': proposal,
                'project': proposal.project,
                'freelancer': freelancer,
                'cover_letter': cover_letter,
                'proposed_amount': proposed_amount,
                'estimated_duration': estimated_duration
            }
            
            # Validate proposal data
            is_valid, error_message = ProposalValidator.validate_proposal_data(
                cover_letter=cover_letter,
                proposed_amount=proposed_amount,
                estimated_duration=estimated_duration,
                attachments=attachments,
                project=proposal.project
            )
            
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME, context)
            
            # Update proposal
            proposal.cover_letter = cover_letter
            proposal.proposed_amount = proposed_amount
            proposal.estimated_duration = estimated_duration
            proposal.save()
            
            # Handle new attachments
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'proposal_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProposalAttachment.objects.create(
                        proposal=proposal,
                        file=os.path.basename(filename)
                    )
            
            # Handle deleted attachments
            deleted_attachments = request.POST.get('deleted_attachments', '').split(',')
            if deleted_attachments and deleted_attachments[0]:  # Check if there are any deleted attachments
                for attachment_id in deleted_attachments:
                    try:
                        attachment = ProposalAttachment.objects.get(id=attachment_id, proposal=proposal)
                        # Delete the file from storage
                        if os.path.exists(attachment.file.path):
                            os.remove(attachment.file.path)
                        attachment.delete()
                    except (ProposalAttachment.DoesNotExist, Exception) as e:
                        print(f"[Delete Attachment Error]: {e}")
                        continue
            
            # Send notification to client about update
            client_notification_url = reverse('project:project-proposals', kwargs={'project_id': proposal.project.id})
            NotificationManager.send_notification(
                user=proposal.project.client.user,
                message=f"A proposal for your project '{proposal.project.title}' has been updated by {freelancer.user.get_full_name()}",
                redirect_url=client_notification_url
            )
            
            messages.success(request, 'Your proposal has been updated successfully!')
            return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))
            
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to edit it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[EditProposalView POST Error]: {e}")
            messages.error(request, 'Something went wrong while updating your proposal.')
            return redirect(reverse('proposal:edit-proposal', kwargs={'proposal_id': proposal_id}))

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: WithdrawProposalView
# Description: Handles withdrawal of pending proposals
# Tested On:
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class WithdrawProposalView(BaseProposalView):
    """
    - Handles withdrawal of pending proposals
    - Updates proposal status and sends notifications
    """
    PROPOSAL_URL = 'proposal:freelancer-proposal-detail'
    PROPOSALS_URL = 'proposal:freelancer-proposals'

    def get(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.get(id=proposal_id, freelancer=freelancer)
            
            # Validate proposal can be withdrawn
            if proposal.status != Proposal.Status.PENDING:
                messages.error(request, 'Only pending proposals can be withdrawn.')
                return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))
            
            # Update proposal status to withdrawn
            proposal.status = Proposal.Status.WITHDRAWN
            proposal.save()
            
            # Send notification to client
            client_notification_url = reverse('project:project-proposals', kwargs={'project_id': proposal.project.id})
            NotificationManager.send_notification(
                user=proposal.project.client.user,
                message=f"A proposal for your project '{proposal.project.title}' has been withdrawn by {freelancer.user.get_full_name()}",
                redirect_url=client_notification_url
            )
            
            messages.success(request, 'Your proposal has been withdrawn successfully.')
            return redirect(self.PROPOSALS_URL)
            
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to withdraw it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[WithdrawProposalView Error]: {e}")
            messages.error(request, 'Something went wrong while withdrawing your proposal.')
            return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal_id}))

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: ClientProjectProposalsView
# Description: Shows proposals for a client's project
# Tested On:
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class ClientProjectProposalsView(CustomLoginRequiredMixin, View):
    """
    - Displays proposals submitted for a client's project
    - Provides filtering and sorting options
    """
    TEMPLATE_NAME = 'proposals/project-proposals.html'
    PROJECT_URL = 'project:client-project-detail'
    CLIENT_PROJECTS_URL = 'project:client-projects'
    ITEMS_PER_PAGE = 10
    
    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user has client role before proceeding.
        """
        
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        if not hasattr(request.user, 'role') or request.user.role != 'client':
            messages.error(request, "Access denied. You must be a client to view this page.")
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, project_id):
        try:
            from projects.models import Client
            
            # Get client and project
            client = Client.objects.get(user=request.user)
            project = get_object_or_404(Project, id=project_id, client=client)
            
            # Get proposals for the project
            proposals_list = Proposal.objects.filter(project=project).order_by('-created_at')
            
            # Get filter values from request
            selected_statuses = request.GET.getlist('status')
            sort_by = request.GET.get('sort', '-created_at')
            keyword = request.GET.get('search')
            
            # Search by keyword
            if keyword:
                proposals_list = proposals_list.filter(
                    Q(freelancer__user__first_name__icontains=keyword) |
                    Q(freelancer__user__last_name__icontains=keyword) |
                    Q(freelancer__skills__name__icontains=keyword) |
                    Q(cover_letter__icontains=keyword)
                ).distinct()
            
            # Filter by status
            if selected_statuses and 'all' not in selected_statuses:
                proposals_list = proposals_list.filter(status__in=selected_statuses)
            
            # Sort proposals
            valid_sort_fields = ['created_at', '-created_at', 'proposed_amount', '-proposed_amount', 
                                 'estimated_duration', '-estimated_duration']
            if sort_by in valid_sort_fields:
                proposals_list = proposals_list.order_by(sort_by)
            
            # Pagination
            paginator = Paginator(proposals_list, self.ITEMS_PER_PAGE)
            page_number = request.GET.get('page')
            proposals = paginator.get_page(page_number)
            
            context = {
                'project': project,
                'proposals': proposals,
                'status_choices': Proposal.Status.choices,
                'selected_statuses': selected_statuses,
                'sort_by': sort_by,
                'search_keyword': keyword,
            }
            return render(request, self.TEMPLATE_NAME, context)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to view it.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[ClientProjectProposalsView Error]: {e}")
            messages.error(request, 'Something went wrong while loading proposals.')
            return redirect(self.CLIENT_PROJECTS_URL)