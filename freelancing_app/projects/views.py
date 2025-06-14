from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from notification.utils import NotificationManager
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from datetime import date, timedelta
from contract.models import Contract
from django.contrib import messages
from django.db.models import Q, Avg
from django.conf import settings
from django.urls import reverse
from django.views import View
from proposals.models import *
from .models import *
from .utils import *
import json
import os

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseProjectView
# Description: Base class for project-related views with utility methods
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseProjectView(CustomLoginRequiredMixin, View):
    """
    Base class for project-related views. Provides utility methods and constants.
    Restricts access to users with the 'client' role.
    """
    HOME_URL = 'home:home'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user has client role before proceeding.
        """
        
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        if not hasattr(request.user, 'role') or request.user.role != 'client':
            messages.error(request, "Access denied. You must be a client to view this page.")
            return redirect(self.HOME_URL)
        return super().dispatch(request, *args, **kwargs)
    
    def get_client(self, request):
        """
        Get client instance for the logged-in user.
        """
        return Client.objects.get(user=request.user)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: NewProjectView
# Description: Handles creation of new projects (both draft and published)
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class NewProjectView(BaseProjectView):
    """
    - Handles creation of new projects (both draft and published)
    - Manages project details, attachments, and notifications
    """
    TEMPLATE_NAME = 'projects/newproject.html'
    NEW_PROJECT_URL = 'project:new-project'
    PROJECT_URL = 'project:client-project-detail'

    def get(self, request):
        try:
            client = self.get_client(request)
            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices
            project_skills_levels = ProjectSkill.SkillLevel.choices
            
            return render(request, self.TEMPLATE_NAME, {
                'client': client,
                'skills': skills,
                'categories': categories,
                'experience_levels': experience_levels,
                'project_skills_levels': project_skills_levels
            })
            
        except Exception as e:
            print(f"[NewProjectView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.HOME_URL)
    
    def post(self, request):
        try:
            client = self.get_client(request)
            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices
            project_skills_levels = ProjectSkill.SkillLevel.choices

            # Get form data
            title = request.POST.get('title', '').strip()
            category_id = request.POST.get('category')
            experience_level = request.POST.get('experience_level')
            estimated_duration = request.POST.get('estimated_duration')
            budget_type = request.POST.get('budget_type')
            is_price_range = (budget_type == 'range')
            selected_skill_ids = [int(sid) for sid in request.POST.getlist('skills')]
            
            skill_levels_map = {
                int(skill_id): request.POST.get(f'skill_level_{skill_id}', ProjectSkill.SkillLevel.INTERMEDIATE)
                for skill_id in selected_skill_ids
            }
            
            # Handle budget fields
            fixed_budget = None
            budget_min = None
            budget_max = None
            if is_price_range:
                budget_min = request.POST.get('budget_min')
                budget_max = request.POST.get('budget_max')
            else:
                fixed_budget = request.POST.get('fixed_budget')
                
            description = request.POST.get('description', '').strip()
            
            # Handle key requirements as a list
            key_requirements = request.POST.get('key_requirements', '').strip()
            if key_requirements:
                key_requirements = '\n'.join([req.strip() for req in key_requirements.split('\n') if req.strip()])
                
            print(f"Key Requirements: {key_requirements}")
                            
            additional_info = request.POST.get('additional_info', '').strip()
            attachments = request.FILES.getlist('attachment[]')
            status = request.POST.get('status', 'draft')
            
            # Prepare context for form re-rendering
            context = {
                'skills': skills,
                'skills_select': selected_skill_ids,
                'skill_levels_map': skill_levels_map,
                'title': title,
                'category_id': int(category_id) if category_id else None,
                'experience_level': experience_level,
                'estimated_duration': int(estimated_duration) if estimated_duration else None,
                'is_price_range': is_price_range,
                'fixed_budget': float(fixed_budget) if fixed_budget else None,
                'budget_min': float(budget_min) if budget_min else None,
                'budget_max': float(budget_max) if budget_max else None,
                'description': description,
                'key_requirements': key_requirements,
                'additional_info': additional_info,
                'attachments': attachments,
                'client': client,
                'categories': categories,
                'experience_levels': experience_levels,
                'project_skills_levels': project_skills_levels
            }
            
            # Validate project data
            is_valid, error_message = ProjectValidator.validate_project_data(
                title=title,
                category_id=category_id,
                experience_level=experience_level,
                estimated_duration=estimated_duration,
                is_price_range=is_price_range,
                fixed_budget=fixed_budget,
                budget_min=budget_min,
                budget_max=budget_max,
                description=description,
                key_requirements=key_requirements,
                additional_info=additional_info,
                selected_skills=selected_skill_ids,
                attachments=attachments,
                request=request
            )
            
            if not is_valid:
                messages.error(request, error_message)
                print("checking requirements", key_requirements)
                return render(request, self.TEMPLATE_NAME, context)
            
            # Determine project status and notification
            title_short = (title[:30] + '...') if len(title) > 30 else title
            if status == 'posted':
                notification_message = f"Your project {title_short} has been successfully published and is now visible to freelancers."
                project_status = Project.Status.PUBLISHED
                success_message = 'Your project has been successfully published and is now live.'
            else:
                notification_message = f"Your project {title_short} has been saved as a draft. You can publish it anytime later."
                project_status = Project.Status.DRAFT
                success_message = 'Your project has been saved as a draft.'
                
            # Create project
            project = Project.objects.create(
                client=client,
                title=title,
                description=description,
                key_requirements=key_requirements,
                additional_info=additional_info,
                category_id=category_id,
                experience_level=experience_level,
                estimated_duration=estimated_duration,
                is_fixed_price=not is_price_range,
                fixed_budget=fixed_budget,
                budget_min=budget_min,
                budget_max=budget_max,
                status=project_status
            )
            
            for skill_id in selected_skill_ids:
                skill = Skill.objects.get(id=skill_id)
                level = request.POST.get(f'skill_level_{skill_id}', ProjectSkill.SkillLevel.INTERMEDIATE)
                ProjectSkill.objects.create(
                    project=project,
                    skill=skill,
                    level=level
                )
            
            # Handle attachments
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'project_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProjectAttachment.objects.create(
                        project=project,
                        file='project_attachments/' + os.path.basename(filename)  
                    )
                    
            # Send notification
            project_detail_url = reverse(self.PROJECT_URL, kwargs={'project_id': project.id})
            NotificationManager.send_notification(
                user=request.user,
                message=notification_message,
                redirect_url=project_detail_url
            )
            
            messages.success(request, success_message)
            return redirect(project_detail_url)
            
        except Exception as e:
            print(f"[NewProjectView POST Error]: {e}")
            messages.error(request, 'Something went wrong while creating your project.')
            return redirect(self.NEW_PROJECT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ClientProjectsView
# Description: Displays and filters client's projects
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ClientProjectsView(BaseProjectView):
    """
    - Displays paginated list of client's projects
    - Provides filtering by status, category, experience, budget, and duration
    - Includes search functionality
    """
    TEMPLATE_NAME = 'projects/projects.html'
    ITEMS_PER_PAGE = 10

    def get(self, request):
        try:    
            client = self.get_client(request)
            projects_list = Project.objects.filter(client=client).prefetch_related(
                'proposals__freelancer__user'
            ).order_by('-created_at')
            categories = ProjectCategory.objects.all().order_by('name')
            
            # Get filter values from request
            selected_statuses = request.GET.getlist('status')
            selected_categories = request.GET.getlist('category')
            selected_experience = request.GET.getlist('experience')
            selected_budgets = request.GET.getlist('budget')
            selected_durations = request.GET.getlist('duration')
            keyword = request.GET.get('search')
            
            # Search by keyword
            if keyword:
                projects_list = projects_list.filter(
                    Q(title__icontains=keyword) |
                    Q(status__icontains=keyword) |
                    Q(category__name__icontains=keyword) |
                    Q(experience_level__icontains=keyword) |
                    Q(estimated_duration__icontains=keyword)
                )
                
            # Filter by status
            if selected_statuses and 'all' not in selected_statuses:
                projects_list = projects_list.filter(status__in=selected_statuses)
                
            # Filter by category
            if selected_categories and 'all' not in selected_categories:
                projects_list = projects_list.filter(category_id__in=selected_categories)
                
            # Filter by experience level
            if selected_experience and 'all' not in selected_experience:
                projects_list = projects_list.filter(experience_level__in=selected_experience)
                
            # Filter by budget
            if selected_budgets and 'all' not in selected_budgets:
                budget_q = Q()
                for b in selected_budgets:
                    if b == '500000+':
                        budget_q |= Q(fixed_budget__gte=500000) | Q(budget_max__gte=500000)
                    else:
                        parts = b.split('-')
                        if len(parts) == 2:
                            min_val, max_val = map(int, parts)
                            budget_q |= (
                                Q(fixed_budget__gte=min_val, fixed_budget__lte=max_val) |
                                Q(budget_min__gte=min_val, budget_max__lte=max_val)
                            )
                projects_list = projects_list.filter(budget_q)
                
            # Filter by duration
            if selected_durations and 'all' not in selected_durations:
                duration_q = Q()
                for d in selected_durations:
                    if d == '12+':
                        duration_q |= Q(estimated_duration__gte=12)
                    else:
                        min_d, max_d = map(int, d.split('-'))
                        duration_q |= Q(estimated_duration__gte=min_d, estimated_duration__lte=max_d)
                projects_list = projects_list.filter(duration_q)
                
            # Pagination
            paginator = Paginator(projects_list, self.ITEMS_PER_PAGE)
            page_number = request.GET.get('page')
            projects = paginator.get_page(page_number)
            
            context = {
                'projects': projects,
                'status_choices': Project.Status.choices,
                'categories': categories,
                'expertise_levels': Project.ExpertiseLevel.choices,
                'selected_statuses': selected_statuses,
                'selected_categories': selected_categories,
                'selected_experience': selected_experience,
                'selected_budgets': selected_budgets,
                'selected_durations': selected_durations,
                'search_keyword': keyword,
                'categories_dict': {str(c.id): c for c in categories},
            }
            return render(request, self.TEMPLATE_NAME, context)
            
        except Exception as e:
            print(f"[ClientProjectsView Error]: {e}")
            messages.error(request, 'Something went wrong while loading your projects.')
            return redirect(self.HOME_URL)
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ClientProjectDetailView
# Description: Displays detailed view of a client's project
# Tested On: 2025-04-28
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class ClientProjectDetailView(BaseProjectView):
    """
    - Shows detailed view of a client's project
    - Includes project info, skills, attachments, and management options
    """
    TEMPLATE_NAME = 'projects/project-detail.html'
    PROJECT_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.prefetch_related(
                'project_skills__skill',
                'project_attachments'
            ).get(id=project_id, client=client)
            
            attachments = []
            for attachment in project.project_attachments.all():
                try:
                    filename = os.path.basename(attachment.file.name)
                    file_path = os.path.join(settings.MEDIA_ROOT, 'project_attachments', filename)
                    
                    if os.path.exists(file_path):
                        if attachment.file.name != os.path.join('project_attachments', filename):
                            attachment.file.name = os.path.join('project_attachments', filename)
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
                            
            key_requirements = []
            if project.key_requirements:
                key_requirements = [req.strip() for req in project.key_requirements.split('\n') if req.strip()]
                
            shortlisted_count = project.proposals.filter(is_shortlisted=True).count()
            avg_bid_amount = project.proposals.aggregate(avg_amount=Avg('proposed_amount'))['avg_amount'] or 0

            context = {
                'project': project,
                'client': client,
                'attachments': attachments,  
                'key_requirements': key_requirements,
                'shortlisted_count': shortlisted_count,
                'avg_bid_amount': avg_bid_amount
            }
            
            return render(request, self.TEMPLATE_NAME, context)
            
        except Project.DoesNotExist:
            messages.error(request, 'The project you are trying to access does not exist.')
            return redirect(self.PROJECT_URL)
        except Exception as e:
            print(f"[ClientProjectDetailView Error]: {e}")
            messages.error(request, 'Something went wrong while loading the project.')
            return redirect(self.PROJECT_URL)
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PublishProjectView
# Description: Handles publishing of draft projects
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PublishProjectView(BaseProjectView):
    """
    - Handles publishing of draft projects
    - Validates project meets requirements before publishing
    - Sends notification to client
    """
    PROJECT_URL = 'project:client-project-detail'
    CLIENT_PROJECTS_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)

            # Validate project can be published
            if project.status != Project.Status.DRAFT:
                messages.warning(request, 'Only draft projects can be published.')
                return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project.id}))
            
            # Update project status to published
            project.status = Project.Status.PUBLISHED
            project.save()

            # Send notification
            title_short = (project.title[:30] + '...') if len(project.title) > 30 else project.title
            project_detail_url = reverse(self.PROJECT_URL, kwargs={'project_id': project.id})
            NotificationManager.send_notification(
                user=request.user,
                message=f"Your project {title_short} has been successfully published and is now visible to freelancers.",
                redirect_url=project_detail_url
            )

            messages.success(request, 'Your project has been successfully published and is now live!')
            return redirect(project_detail_url)

        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to publish it.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[PublishProjectView Error]: {e}")
            messages.error(request, 'Something went wrong while publishing your project.')
            return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project_id}))
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: EditProjectView
# Description: Handles editing of existing projects
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class EditProjectView(BaseProjectView):
    """
    - Handles editing of existing projects
    - Uses similar logic to NewProjectView but with existing project data
    - Prevents editing of non-draft projects
    """
    TEMPLATE_NAME = 'projects/editproject.html'
    PROJECT_URL = 'project:client-project-detail'
    CLIENT_PROJECTS_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.prefetch_related(
                'project_skills__skill',
                'project_attachments'
            ).get(id=project_id, client=client)

            # Don't allow editing of non-draft projects
            if project.status != Project.Status.DRAFT:
                messages.warning(request, 'Only draft projects can be edited.')
                return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project.id}))

            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices
            project_skills_levels = ProjectSkill.SkillLevel.choices

            # Get existing project skills and levels
            skill_levels_map = {
                ps.skill.id: ps.level 
                for ps in project.project_skills.all()
            }

            # Format key requirements for display
            key_requirements = []
            if project.key_requirements:
                key_requirements = [req.strip() for req in project.key_requirements.split('\n') if req.strip()]
                key_requirements = [req.replace('\n', ' ').strip() for req in key_requirements]
            key_requirements = '\n'.join(key_requirements)

            # Prepare existing attachments
            existing_attachments = []
            if project.project_attachments.all():
                for attachment in project.project_attachments.all():
                    try:
                        # Get the file path relative to MEDIA_ROOT
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
                'project': project,
                'skills': skills,
                'skills_select': list(skill_levels_map.keys()),
                'skill_levels_map': skill_levels_map,
                'categories': categories,
                'experience_levels': experience_levels,
                'project_skills_levels': project_skills_levels,
                'key_requirements': key_requirements,
                'existing_attachments_json': json.dumps(existing_attachments),
            }
            
            return render(request, self.TEMPLATE_NAME, context)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to edit it.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[EditProjectView GET Error]: {e}")
            messages.error(request, 'Something went wrong while loading the project for editing.')
            return redirect(self.CLIENT_PROJECTS_URL)

    def post(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)

            # Don't allow editing of non-draft projects
            if project.status != Project.Status.DRAFT:
                messages.error(request, 'Only draft projects can be edited.')
                return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project.id}))

            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices
            project_skills_levels = ProjectSkill.SkillLevel.choices

            # Get form data (same as NewProjectView)
            title = request.POST.get('title', '').strip()
            category_id = request.POST.get('category')
            experience_level = request.POST.get('experience_level')
            estimated_duration = request.POST.get('estimated_duration')
            budget_type = request.POST.get('budget_type')
            is_price_range = (budget_type == 'range')
            selected_skill_ids = [int(sid) for sid in request.POST.getlist('skills')]
            
            skill_levels_map = {
                int(skill_id): request.POST.get(f'skill_level_{skill_id}', ProjectSkill.SkillLevel.INTERMEDIATE)
                for skill_id in selected_skill_ids
            }
            
            # Handle budget fields
            fixed_budget = None
            budget_min = None
            budget_max = None
            if is_price_range:
                budget_min = request.POST.get('budget_min')
                budget_max = request.POST.get('budget_max')
            else:
                fixed_budget = request.POST.get('fixed_budget')
                
            description = request.POST.get('description', '').strip()
            
            # Handle key requirements as a list
            key_requirements = request.POST.get('key_requirements', '').strip()
            if key_requirements:
                key_requirements = '\n'.join([req.strip() for req in key_requirements.split('\n') if req.strip()])
                                
            additional_info = request.POST.get('additional_info', '').strip()
            attachments = request.FILES.getlist('attachment[]')
            status = request.POST.get('status', 'draft')
            
            # Prepare context for form re-rendering
            context = {
                'project': project,
                'skills': skills,
                'skills_select': selected_skill_ids,
                'skill_levels_map': skill_levels_map,
                'title': title,
                'category_id': int(category_id) if category_id else None,
                'experience_level': experience_level,
                'estimated_duration': int(estimated_duration) if estimated_duration else None,
                'is_price_range': is_price_range,
                'fixed_budget': float(fixed_budget) if fixed_budget else None,
                'budget_min': float(budget_min) if budget_min else None,
                'budget_max': float(budget_max) if budget_max else None,
                'description': description,
                'key_requirements': key_requirements,
                'additional_info': additional_info,
                'attachments': attachments,
                'client': client,
                'categories': categories,
                'experience_levels': experience_levels,
                'project_skills_levels': project_skills_levels
            }
            
            # Validate project data
            is_valid, error_message = ProjectValidator.validate_project_data(
                title=title,
                category_id=category_id,
                experience_level=experience_level,
                estimated_duration=estimated_duration,
                is_price_range=is_price_range,
                fixed_budget=fixed_budget,
                budget_min=budget_min,
                budget_max=budget_max,
                description=description,
                key_requirements=key_requirements,
                additional_info=additional_info,
                selected_skills=selected_skill_ids,
                attachments=attachments,
                request=request
            )
            
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME, context)
            
            # Update project
            project.title = title
            project.description = description
            project.key_requirements = key_requirements
            project.additional_info = additional_info
            project.category_id = category_id
            project.experience_level = experience_level
            project.estimated_duration = estimated_duration
            project.is_fixed_price = not is_price_range
            project.fixed_budget = fixed_budget
            project.budget_min = budget_min
            project.budget_max = budget_max
            
            # Only update status if posting (not saving as draft)
            title_short = (title[:30] + '...') if len(title) > 30 else title
            if status == 'posted':
                project.status = Project.Status.PUBLISHED
                notification_message = f"Your project {title_short} has been successfully published and is now visible to freelancers."
                success_message = 'Your project has been successfully published and is now live.'
            else:
                notification_message = f"Your project {title_short} has been updated and saved as a draft."
                success_message = 'Your project has been updated and saved as a draft.'
            
            project.save()
            
            # Update skills - first remove old ones
            ProjectSkill.objects.filter(project=project).delete()
            for skill_id in selected_skill_ids:
                skill = Skill.objects.get(id=skill_id)
                level = request.POST.get(f'skill_level_{skill_id}', ProjectSkill.SkillLevel.INTERMEDIATE)
                ProjectSkill.objects.create(
                    project=project,
                    skill=skill,
                    level=level
                )
            
            # Handle new attachments
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'project_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProjectAttachment.objects.create(
                        project=project,
                        file='project_attachments/' + os.path.basename(filename)  
                    )

            # Handle deleted attachments
            deleted_attachments = request.POST.get('deleted_attachments', '').split(',')
            if deleted_attachments and deleted_attachments[0]:  # Check if there are any deleted attachments
                for attachment_id in deleted_attachments:
                    try:
                        attachment = ProjectAttachment.objects.get(id=attachment_id, project=project)
                        # Delete the file from storage
                        if os.path.exists(attachment.file.path):
                            os.remove(attachment.file.path)
                        attachment.delete()
                    except (ProjectAttachment.DoesNotExist, Exception) as e:
                        print(f"[Delete Attachment Error]: {e}")
                        continue
                    
            # Send notification
            project_detail_url = reverse(self.PROJECT_URL, kwargs={'project_id': project.id})
            NotificationManager.send_notification(
                user=request.user,
                message=notification_message,
                redirect_url=project_detail_url
            )
            
            messages.success(request, success_message)
            return redirect(project_detail_url)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to edit it.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[EditProjectView POST Error]: {e}")
            messages.error(request, 'Something went wrong while updating your project.')
            return redirect(reverse('project:edit-project', kwargs={'project_id': project_id}))
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: DeleteProjectView
# Description: Handles deletion of existing projects
# Tested On: 2025-04-28
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteProjectView(BaseProjectView):
    """
    - Handles deletion of existing projects
    - Only allows deletion of draft projects or projects without accepted proposals
    - Deletes associated attachments and skills
    """
    PROJECT_URL = 'project:client-project-detail'
    CLIENT_PROJECTS_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)

            # Check if project can be deleted (only drafts or projects without accepted proposals)
            if project.status != Project.Status.DRAFT and project.proposals.filter(status='accepted').exists():
                messages.error(request, 'Cannot delete this project as it has accepted proposals.')
                return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project.id}))

            # Delete project attachments first
            attachments = project.project_attachments.all()
            for attachment in attachments:
                try:
                    file_path = os.path.join(settings.MEDIA_ROOT, str(attachment.file))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"[Delete Attachment Error]: {e}")
                attachment.delete()

            # Delete the project
            project_title = project.title
            project.delete()

            # Send notification
            title_short = (project_title[:30] + '...') if len(project_title) > 30 else project_title
            NotificationManager.send_notification(
                user=request.user,
                message=f"Your project {title_short} has been successfully deleted.",
                redirect_url=reverse(self.CLIENT_PROJECTS_URL)
            )

            messages.success(request, 'Project has been successfully deleted.')
            return redirect(self.CLIENT_PROJECTS_URL)

        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to delete it.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[DeleteProjectView Error]: {e}")
            messages.error(request, 'Something went wrong while deleting the project.')
            return redirect(reverse(self.PROJECT_URL, kwargs={'project_id': project_id}))
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: SetHiringView
# Description: Handles changing project status to hiring
# Tested On: 
# Status: 
# Code Refractor Status: 
# ------------------------------------------------------
class SetHiringView(BaseProjectView):
    """
    - Handles changing project status to hiring
    - Prevents new proposals from being submitted
    """
    PROJECT_URL = 'project:client-project-detail'
    CLIENT_PROJECTS_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)
            
            # Only allow status change from published to hiring
            if project.status != Project.Status.PUBLISHED:
                messages.error(request, 'Only published projects can be set to hiring status.')
                return redirect(self.PROJECT_URL, project_id=project_id)
            
            # Update project status
            project.status = Project.Status.HIRING
            project.save()
            
            messages.success(request, 'Project status has been updated to hiring. No new proposals will be accepted.')
            return redirect(self.PROJECT_URL, project_id=project_id)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect(self.CLIENT_PROJECTS_URL)
        except Exception as e:
            print(f"[SetHiringView Error]: {e}")
            messages.error(request, 'An error occurred while updating the project status.')
            return redirect(self.CLIENT_PROJECTS_URL)
        
# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ProjectProposalsView
# Description: Displays all proposals for a client's project
# Tested On: 2025-04-29
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProjectProposalsView(BaseProjectView):
    """
    - Displays all proposals for a specific project owned by the client
    - Provides filtering by status, shortlisted status, and sorting options
    - Shows proposal details including attachments
    """
    TEMPLATE_NAME = 'projects/project-proposals.html'
    ITEMS_PER_PAGE = 10
    PROJECT_URL = 'project:client-projects'

    def get(self, request, project_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)
            proposals = Proposal.objects.filter(project=project).select_related(
                'freelancer__user'
            ).prefetch_related(
                'attachments'
            ).order_by('-submitted_at')
            
            # Get filter values from request
            keyword = request.GET.get('search')
            selected_statuses = request.GET.getlist('status')
            selected_budgets = request.GET.getlist('budget')
            selected_experience = request.GET.getlist('experience')
            selected_availability = request.GET.getlist('availability')
            selected_durations = request.GET.getlist('duration')
            is_shortlisted = request.GET.get('shortlisted') == 'true'

            # Apply filters
            if keyword:
                proposals = proposals.filter(
                    Q(cover_letter__icontains=keyword) |
                    Q(approach_methodology__icontains=keyword) |
                    Q(relevant_experience__icontains=keyword) |
                    Q(questions_for_client__icontains=keyword) |
                    Q(freelancer__user__full_name__icontains=keyword)
                )

            if selected_statuses:
                proposals = proposals.filter(status__in=selected_statuses)

            if selected_budgets:
                budget_filters = Q()
                for budget in selected_budgets:
                    if budget == '0-50000':
                        budget_filters |= Q(proposed_amount__lte=50000)
                    elif budget == '50000-100000':
                        budget_filters |= Q(proposed_amount__gt=50000, proposed_amount__lte=100000)
                    elif budget == '100000-500000':
                        budget_filters |= Q(proposed_amount__gt=100000, proposed_amount__lte=500000)
                    elif budget == '500000+':
                        budget_filters |= Q(proposed_amount__gt=500000)
                proposals = proposals.filter(budget_filters)

            if selected_experience:
                proposals = proposals.filter(freelancer__experience_level__in=selected_experience)

            if selected_availability:
                proposals = proposals.filter(freelancer__availability__in=selected_availability)

            if selected_durations:
                duration_filters = Q()
                for duration in selected_durations:
                    if duration == '0-4':
                        duration_filters |= Q(estimated_duration__lte=4)
                    elif duration == '4-12':
                        duration_filters |= Q(estimated_duration__gt=4, estimated_duration__lte=12)
                    elif duration == '12+':
                        duration_filters |= Q(estimated_duration__gt=12)
                proposals = proposals.filter(duration_filters)

            if is_shortlisted:
                proposals = proposals.filter(is_shortlisted=True)

            # Pagination
            paginator = Paginator(proposals, self.ITEMS_PER_PAGE)
            page_number = request.GET.get('page')
            proposals = paginator.get_page(page_number)

            context = {
                'project': project,
                'proposals': proposals,
                'status_choices': Proposal.Status.choices,
                'freelancer_experience_levels': Freelancer.ExpertiseLevel.choices,
                'freelancer_availability_choices': Freelancer.Availability.choices,
                'selected_statuses': selected_statuses,
                'selected_budgets': selected_budgets,
                'selected_experience': selected_experience,
                'selected_availability': selected_availability,
                'selected_durations': selected_durations,
                'is_shortlisted': is_shortlisted,
            }

            return render(request, self.TEMPLATE_NAME, context)

        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect(self.PROJECT_URL)
        except Exception as e:
            print(f"[ProjectProposalsView Error]: {e}")
            messages.error(request, 'An error occurred while loading proposals.')
            return redirect(self.PROJECT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ProposalDetailView
# Description: Displays detailed view of a specific proposal
# Tested On: 2025-04-29
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProjectProposalDetailsView(BaseProjectView):
    """
    - Shows detailed view of a specific proposal
    - Includes proposal info, attachments, freelancer details, and management options
    """
    TEMPLATE_NAME = 'projects/project-proposal-details.html'
    PROJECT_URL = 'project:client-projects'
    PROPOSAL_DETAIL_URL = 'project:project-proposal-details'
    ALLOWED_ACTIONS = ['accept', 'reject', 'shortlist']

    def get(self, request, project_id, proposal_id):
        try:
            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)
            proposal = Proposal.objects.select_related(
                'freelancer__user',
                'project'
            ).prefetch_related(
                'attachments'
            ).get(id=proposal_id, project=project)
            
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
            
            context = {
                'project': project,
                'proposal': proposal,
                'attachments': attachments,
            }
            
            return render(request, self.TEMPLATE_NAME, context)
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found or you do not have permission to view this proposal.')
            return redirect(self.PROJECT_URL)
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found or you do not have permission to view it.')
            return redirect(self.PROJECT_URL)
        except Exception as e:
            print(f"[ProposalDetailView Error]: {e}")
            messages.error(request, 'Something went wrong while loading the proposal details.')
            return redirect(self.PROJECT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ProposalActionView
# Description: Handles actions on proposals (accept, shortlist, reject)
# Tested On:  2025-04-29
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProposalActionView(BaseProjectView):
    """
    - Handles actions on proposals (accept, shortlist, reject)
    - Validates action and updates proposal status
    - Sends notifications to freelancer
    """
    FREELANCER_PROPOSAL_DETAILS_URL = 'proposal:freelancer-proposal-detail'
    PROJECT_PROPOSAL_DETAILS_URL = 'project:project-proposal-details'
    PROJECT_PROPOSALS_URL = 'project:project-proposals'
    PROJECT_URL = 'project:client-projects'
    ALLOWED_ACTIONS = ['accept', 'shortlist', 'reject']

    def post(self, request, project_id, proposal_id, action):
        try:
            if action not in self.ALLOWED_ACTIONS:
                messages.error(request, 'Invalid action specified.')
                return redirect(self.PROJECT_PROPOSALS_URL, project_id=project_id)

            client = self.get_client(request)
            project = Project.objects.get(id=project_id, client=client)
            proposal = Proposal.objects.get(id=proposal_id, project=project)

            if proposal.status != 'pending':
                messages.error(request, f'Cannot {action} a proposal that is not pending.')
                return redirect(self.PROJECT_PROPOSAL_DETAILS_URL, project_id=project_id, proposal_id=proposal_id)

            if action == 'accept':
                proposal.status = Proposal.Status.ACCEPTED
                proposal.is_shortlisted = False
                proposal.save()
                
                Proposal.objects.filter(
                    project=project,
                    status=Proposal.Status.PENDING
                ).exclude(id=proposal.id).update(status=Proposal.Status.REJECTED)
                
                start_date = date.today()
                end_date = start_date + timedelta(weeks=project.estimated_duration)
                
                contract = Contract.objects.create(
                    proposal=proposal,
                    agreed_amount=proposal.proposed_amount,
                    start_date=start_date,
                    end_date=end_date,
                    status=Contract.Status.ACTIVE,
                    client_signature=False,  
                    freelancer_signature=False,  
                )
                
                project.status = Project.Status.IN_PROGRESS
                project.save()
                
                short_title = (project.title[:30] + '...') if len(project.title) > 30 else project.title
                client_contract_url = reverse('contract:client_contract_detail', kwargs={'contract_id': contract.id})
                freelancer_contract_url = reverse('contract:freelancer_contract_detail', kwargs={'contract_id': contract.id})
                
                # Send notification to freelancer
                NotificationManager.send_notification(
                    user=proposal.freelancer.user,
                    message=f'Your proposal for project {short_title} has been accepted! A contract has been created.',
                    redirect_url=freelancer_contract_url
                )
                
                # Send notification to client
                NotificationManager.send_notification(
                    user=request.user,
                    message=f'You have accepted a proposal for project {short_title}. A contract has been created.',
                    redirect_url=client_contract_url
                )
                
                messages.success(request, 'Proposal accepted and contract created successfully.')
                return redirect(client_contract_url)
                
            elif action == 'shortlist':
                proposal.is_shortlisted = not proposal.is_shortlisted
                proposal.save()

                short_title = (project.title[:30] + '...') if len(project.title) > 30 else project.title
                NotificationManager.send_notification(
                    user=proposal.freelancer.user,
                    message=f'Your proposal for project {short_title} has been {"shortlisted" if proposal.is_shortlisted else "removed from shortlist"}.',
                    redirect_url=reverse(self.FREELANCER_PROPOSAL_DETAILS_URL, kwargs= {'proposal_id': proposal_id})
                )

                messages.success(request, f'Proposal {"shortlisted" if proposal.is_shortlisted else "removed from shortlist"} successfully.')
                return redirect(self.PROJECT_PROPOSAL_DETAILS_URL, project_id=project_id, proposal_id=proposal_id)
            
            else:
                proposal.status = Proposal.Status.REJECTED
                proposal.is_shortlisted = False  
                proposal.save()

                short_title = (project.title[:30] + '...') if len(project.title) > 30 else project.title
                NotificationManager.send_notification(
                    user=proposal.freelancer.user,
                    message=f'Your proposal for project {short_title} has been rejected.',
                    redirect_url=reverse(self.FREELANCER_PROPOSAL_DETAILS_URL, kwargs={'proposal_id': proposal_id})
                )
                
                messages.success(request, 'Proposal rejected successfully.')
                return redirect(self.PROJECT_PROPOSAL_DETAILS_URL, project_id=project_id, proposal_id=proposal_id)

        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect(self.PROJECT_URL)
        except Proposal.DoesNotExist:
            messages.error(request, 'Proposal not found.')
            return redirect(self.PROJECT_URL)
        except Exception as e:
            print(f"[ProposalActionView Error]: {e}")
            messages.error(request, 'An error occurred while processing your request.')
            return redirect(self.PROJECT_URL)