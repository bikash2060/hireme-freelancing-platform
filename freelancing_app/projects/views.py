from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import *
from .utils import *
import os
from django.conf import settings

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
            
            if status == 'posted':
                project_status = Project.Status.PUBLISHED
                success_message = 'Project posted successfully!'
            else:
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
                
            messages.success(request, success_message)
            if status == 'posted':
                return redirect(self.home_url)
            else:
                return redirect(self.home_url)
                
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.new_project_url)