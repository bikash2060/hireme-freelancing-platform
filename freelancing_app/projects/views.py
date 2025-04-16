from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import render, redirect
from notification.utils import NotificationManager
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.views import View
from .models import *
from .utils import *
import os

class ClientProjectsView(CustomLoginRequiredMixin, View):
    template_name = 'projects/projects.html'
    home_url = 'home:home'
    items_per_page = 10
    
    def get(self, request):
        try:           
            client = Client.objects.get(user=request.user)
            projects_list = Project.objects.filter(client=client).order_by('-created_at')
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
                
            if selected_experience and 'all' not in selected_experience:
                projects_list = projects_list.filter(experience_level__in=selected_experience)
                
            # Filter by budget
            if selected_budgets and 'all' not in selected_budgets:
                budget_q = Q()
                for b in selected_budgets:
                    if b == '500000+':
                        budget_q |= models.Q(fixed_budget__gte=500000) | models.Q(budget_max__gte=500000)
                    else:
                        parts = b.split('-')
                        if len(parts) == 2:
                            min_val, max_val = map(int, parts)
                            budget_q |= (
                                models.Q(fixed_budget__gte=min_val, fixed_budget__lte=max_val) |
                                models.Q(budget_min__gte=min_val, budget_max__lte=max_val)
                            )
                projects_list = projects_list.filter(budget_q)
                
            # Filter by duration
            if selected_durations and 'all' not in selected_durations:
                duration_q = models.Q()
                for d in selected_durations:
                    if d == '12+':
                        duration_q |= models.Q(estimated_duration__gte=12)
                    else:
                        min_d, max_d = map(int, d.split('-'))
                        duration_q |= models.Q(estimated_duration__gte=min_d, estimated_duration__lte=max_d)
                projects_list = projects_list.filter(duration_q)
                
            # Pagination
            paginator = Paginator(projects_list, self.items_per_page)
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
            }
            return render(request, self.template_name, context)
            
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong while loading your projects.')
            return redirect(self.home_url)
        
class NewProjectView(CustomLoginRequiredMixin, View):
    new_project_template = 'projects/newproject.html'
    new_project_url = 'project:new-project'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            user = request.user
            client = Client.objects.get(user=user)
            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices
            return render(request, self.new_project_template, {
                'client': client,
                'skills': skills,
                'categories': categories,
                'experience_levels': experience_levels
            })
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.home_url)
    
    def post(self, request):
        try:
            user = request.user
            client = Client.objects.get(user=user)
            skills = Skill.objects.all().order_by('name')
            categories = ProjectCategory.objects.all().order_by('name')
            experience_levels = Project.ExpertiseLevel.choices

            title = request.POST.get('title').strip()
            category_id = request.POST.get('category')
            experience_level = request.POST.get('experience_level')
            estimated_duration = request.POST.get('estimated_duration')
            budget_type = request.POST.get('budget_type')

            is_price_range = (budget_type == 'range')
            fixed_budget = None
            budget_min = None
            budget_max = None

            if is_price_range:
                budget_min = request.POST.get('budget_min')
                budget_max = request.POST.get('budget_max')
            else:
                fixed_budget = request.POST.get('fixed_budget')
                
            description = request.POST.get('description').strip()
            skills_required = request.POST.getlist('skills_required')
            selected_skills = [int(skill_id) for skill_id in skills_required]
            attachments = request.FILES.getlist('attachment[]')
            status = request.POST.get('status')
            
            context = {
                'title': title,
                'category_id': int(category_id) if category_id else None,
                'experience_level': experience_level,
                'estimated_duration': int(estimated_duration) if estimated_duration else None,
                'is_price_range': is_price_range,
                'fixed_budget': float(fixed_budget) if fixed_budget else None,
                'budget_min': float(budget_min) if budget_min else None,
                'budget_max': float(budget_max) if budget_max else None,
                'description': description,
                'selected_skills': selected_skills,
                'attachments': attachments,
                'client': client,
                'skills': skills,
                'categories': categories,
                'experience_levels': experience_levels
            }
            
            is_valid, error_message = ProjectValidator.validate_project_data(
                title, category_id, experience_level, estimated_duration, is_price_range, fixed_budget, 
                budget_min, budget_max, description, selected_skills, attachments, request
            )
            
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.new_project_template, context)
            
            notification_message = None
            redirect_url = None
            project_status = None
            
            if status == 'posted':
                notification_message = f"Your project \"{title}\" has been published successfully! It's now visible to freelancers."
                redirect_url = None
                project_status = Project.Status.PUBLISHED
                success_message = 'Project posted successfully!'
            else:
                notification_message = f"Your project \"{title}\" has been saved as a draft. You can publish it later."
                redirect_url = None
                project_status = Project.Status.DRAFT
                success_message = 'Draft saved successfully!'
                
            project = Project.objects.create(
                client=client,
                title=title,
                description=description,
                category_id=category_id,
                experience_level=experience_level,
                estimated_duration=estimated_duration,
                is_fixed_price=not is_price_range,
                fixed_budget=fixed_budget,
                budget_min=budget_min,
                budget_max=budget_max,
                status=project_status
            )
            
            project.skills_required.set([int(skill_id) for skill_id in skills_required])
            
            if attachments:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'project_attachments'))
                for attachment in attachments:
                    filename = fs.save(attachment.name, attachment)
                    ProjectAttachment.objects.create(
                        project=project,
                        file=filename.split('/')[-1] 
                    )
                    
            NotificationManager.send_notification(
                user=request.user,
                message=notification_message,
                redirect_url=redirect_url
            )
            
            messages.success(request, success_message)
            if status == 'posted':
                return redirect(self.home_url)
            else:
                return redirect(self.home_url)
                
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.new_project_url)
    