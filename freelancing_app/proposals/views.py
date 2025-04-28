from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from projects.models import Project, ProjectCategory
from notification.utils import NotificationManager
from .models import Proposal, ProposalAttachment
from freelancerprofile.models import Freelancer
from django.core.paginator import Paginator
from .utils import ProposalValidator
from django.contrib import messages
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
# ✅ [TESTED & COMPLETED]
# View Name: SubmitProposalView
# Description: Handles submission of new proposals
# Tested On: 2025-04-28
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class SubmitProposalView(BaseProposalView):
    """
    - Handles submission of new proposals
    - Manages proposal details, attachments, and notifications
    """
    TEMPLATE_NAME = 'proposals/newproposal.html'
    PROJECT_DETAIL_URL = 'home:project-detail'
    PROJECT_PROPOSALS_URL = 'project:project-proposals'
    PROPOSAL_DETAIL_URL = 'proposal:freelancer-proposal-detail'
    
    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            freelancer = self.get_freelancer(request)
            
            # Check if freelancer already submitted a proposal
            if Proposal.objects.filter(project=project, freelancer=freelancer).exists():
                proposal = Proposal.objects.get(project=project, freelancer=freelancer)
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(reverse(self.PROPOSAL_DETAIL_URL, kwargs={'proposal_id': proposal.id}))
                
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
                proposal = Proposal.objects.get(project=project, freelancer=freelancer)
                messages.warning(request, 'You have already submitted a proposal for this project.')
                return redirect(reverse(self.PROPOSAL_DETAIL_URL, kwargs={'proposal_id': proposal.id}))
            
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
            title_short = (project.title[:30] + '...') if len(project.title) > 30 else project.title
            client_notification_url = reverse(self.PROJECT_PROPOSALS_URL, kwargs={'project_id': project.id})
            NotificationManager.send_notification(
                user=project.client.user,
                message=f"New proposal received for your project {title_short} from {freelancer.user.full_name}.",
                redirect_url=client_notification_url
            )
            
            # Send notification to freelancer
            freelancer_notification_url = reverse(self.PROPOSAL_DETAIL_URL, kwargs={'proposal_id': proposal.id})
            NotificationManager.send_notification(
                user=freelancer.user,
                message=f"You have successfully submitted a proposal for {project.title}.",
                redirect_url=freelancer_notification_url
            )
            
            messages.success(request, 'Your proposal has been submitted successfully!')
            return redirect(freelancer_notification_url)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect('home:projects')
            
        except Exception as e:
            print(f"[SubmitProposalView POST Error]: {e}")
            messages.error(request, 'Something went wrong while submitting your proposal.')
            return redirect(self.PROJECT_DETAIL_URL, project_id=project_id)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: FreelancerProposalsView
# Description: Displays and filters freelancer's proposals
# Tested On: 2025-04-28
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
            proposals_list = Proposal.objects.filter(freelancer=freelancer).order_by('-submitted_at')
            categories = ProjectCategory.objects.all().order_by('name')
            
            # Get filter values from request
            keyword = request.GET.get('search')
            selected_statuses = request.GET.getlist('status')
            selected_categories = request.GET.getlist('category')
            selected_budgets = request.GET.getlist('budget')
            selected_durations = request.GET.getlist('duration')
            
            # Search by keyword
            if keyword:
                proposals_list = proposals_list.filter(
                    Q(project__title__icontains=keyword) |
                    Q(cover_letter__icontains=keyword) |
                    Q(proposed_amount__icontains=keyword) |
                    Q(estimated_duration__icontains=keyword) |
                    Q(status__icontains=keyword) |
                    Q(approach_methodology__icontains=keyword) |
                    Q(relevant_experience__icontains=keyword) |
                    Q(questions_for_client__icontains=keyword) 
                )
            
            # Filter by status
            if selected_statuses and 'all' not in selected_statuses:
                proposals_list = proposals_list.filter(status__in=selected_statuses)
                
            # Filter by category
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
            
            # Filter by duration
            if selected_durations and 'all' not in selected_durations:
                duration_q = Q()
                for d in selected_durations:
                    if d == '12+':
                        duration_q |= Q(estimated_duration__gte=12)
                    else:
                        min_d, max_d = map(int, d.split('-'))
                        duration_q |= Q(estimated_duration__gte=min_d, estimated_duration__lte=max_d)
                proposals_list = proposals_list.filter(duration_q)
            
            # Pagination
            paginator = Paginator(proposals_list, self.ITEMS_PER_PAGE)
            page_number = request.GET.get('page')
            proposals_list = paginator.get_page(page_number)
            
            context = {
                'proposals': proposals_list,
                'status_choices': Proposal.Status.choices,
                'categories': categories,
                'selected_statuses': selected_statuses,
                'selected_categories': selected_categories,
                'selected_budgets': selected_budgets,
                'selected_durations': selected_durations,
                'search_keyword': keyword,
                'freelancer': freelancer,
                'categories_dict': {str(c.id): c for c in categories},
            }
            return render(request, self.TEMPLATE_NAME, context)
            
        except Exception as e:
            print(f"[FreelancerProposalsView Error]: {e}")
            messages.error(request, 'Something went wrong while loading your proposals.')
            return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: FreelancerProposalDetailView
# Description: Displays detailed view of a freelancer's proposal
# Tested On: 2025-04-28 
# Status: Working as expected
# Code Refractor Status: 
# ------------------------------------------------------
class FreelancerProposalDetailView(BaseProposalView):
    """
    - Shows detailed view of a freelancer's proposal
    - Includes proposal info, attachments, and management options
    """
    TEMPLATE_NAME = 'proposals/proposal-details.html'
    PROPOSALS_URL = 'proposal:freelancer-proposals'

    def get(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.get(id=proposal_id, freelancer=freelancer)
            
            attachments = []
            for attachment in proposal.attachments.all():
                try:
                    filename = os.path.basename(attachment.file.name)
                    file_path = os.path.join(settings.MEDIA_ROOT, 'proposal_attachments', filename)
                    
                    if os.path.exists(file_path):
                        if attachment.file.name != os.path.join('proposal_attachments', filename):
                            attachment.file.name = os.path.join('proposal_attachments', filename)
                            attachment.save()
                            
                        attachments.append({
                            'file': attachment.file,
                            'filename': filename,
                            'uploaded_at': attachment.uploaded_at
                        })
                    else:
                        print(f"[Attachment Warning]: File not found at {file_path}")
                except Exception as e:
                    print(f"[Attachment Error]: {e}")
                    continue
                
            return render(request, self.TEMPLATE_NAME, {
                'proposal': proposal,
                'freelancer': freelancer,
                'attachments': attachments,
            })
            
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to view it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[FreelancerProposalDetailView Error]: {e}")
            messages.error(request, 'Something went wrong while loading the proposal.')
            return redirect(self.PROPOSALS_URL)

# ------------------------------------------------------
# ⏳ [PENDING TEST] - Will be done in future
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
            # Send Message to freelancer when they try to edit a proposal
            messages.warning(request, 'Editing proposals feature is not available yet.')
            return redirect(self.HOME_URL)
            
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.prefetch_related(
                'attachments'
            ).get(id=proposal_id, freelancer=freelancer)
            
            # Don't allow editing of non-pending proposals
            if proposal.status != Proposal.Status.PENDING:
                messages.error(request, 'Only pending proposals can be edited.')
                return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))
            
            # Prepare existing attachments
            existing_attachments = []
            if proposal.attachments.all():
                for attachment in proposal.attachments.all():
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
            client_notification_url = reverse(self.PROJECT_PROPOSALS_URL, kwargs={'project_id': proposal.project.id})
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
# ✅ [TESTED & COMPLETED]
# View Name: DeleteProposalView
# Description: Handles deletion of existing proposals
# Tested On: 2025-04-28
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteProposalView(BaseProposalView):
    """
    - Handles deletion of existing proposals
    - Only allows deletion of pending proposals
    - Deletes associated attachments
    """
    PROPOSAL_URL = 'proposal:freelancer-proposal-detail'
    PROPOSALS_URL = 'proposal:freelancer-proposals'

    def get(self, request, proposal_id):
        try:
            freelancer = self.get_freelancer(request)
            proposal = Proposal.objects.get(id=proposal_id, freelancer=freelancer)

            # Check if proposal can be deleted (only rejected proposals)
            if proposal.status != Proposal.Status.REJECTED:
                messages.error(request, 'Cannot delete this proposal as it is not rejected.')
                return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal.id}))

            # Delete proposal attachments first
            attachments = proposal.attachments.all()
            for attachment in attachments:
                try:
                    file_path = os.path.join(settings.MEDIA_ROOT, str(attachment.file))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"[Delete Attachment Error]: {e}")
                attachment.delete()

            # Delete the proposal
            proposal_title = proposal.project.title
            proposal.delete()

            # Send notification
            title_short = (proposal_title[:30] + '...') if len(proposal_title) > 30 else proposal_title
            NotificationManager.send_notification(
                user=request.user,
                message=f"Your proposal for {title_short} has been successfully deleted.",
                redirect_url=reverse(self.PROPOSALS_URL)
            )

            messages.success(request, 'Proposal has been successfully deleted.')
            return redirect(self.PROPOSALS_URL)

        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to delete it.')
            return redirect(self.PROPOSALS_URL)
        except Exception as e:
            print(f"[DeleteProposalView Error]: {e}")
            messages.error(request, 'Something went wrong while deleting the proposal.')
            return redirect(reverse(self.PROPOSAL_URL, kwargs={'proposal_id': proposal_id}))