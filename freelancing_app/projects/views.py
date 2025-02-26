from django.shortcuts import render, redirect
from django.views import View
from accounts.mixins import CustomLoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import Project, ProjectCategory, Skill
from home.models import Notification
from .utils import *
from accounts.models import Client

# Testing Complete
class AddNewProjectView(CustomLoginRequiredMixin, View):
    new_project_template = 'projects/addproject.html'
    new_project_url = 'project:add-new-project'
    home_url = 'homes:home'
    
    def get(self, request):
        try:
            project_categories = ProjectCategory.objects.all().order_by('name')
            skills = Skill.objects.all().order_by('name')
            
            context = {
                'project_categories': project_categories,
                'skills': skills,
            }
            return render(request, self.new_project_template, context)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)
        
    def post(self, request):
        try:
            project_categories = ProjectCategory.objects.all().order_by('name')
            skills = Skill.objects.all().order_by('name')
            
            project_name = request.POST.get('project-name').strip()
            project_description = request.POST.get('project-description')
            project_image = request.FILES.get('project-image')  
            project_budget = request.POST.get('project-budget')
            project_duration = request.POST.get('project-duration')
            skills_select = request.POST.getlist('skills-select') 
            project_category = request.POST.get('project-category')
            action = request.POST.get('action') 
            
            context = {
                'project_name': project_name,
                'project_description': project_description,
                'project_budget': project_budget,
                'project_duration': project_duration,
                'skills_select': skills_select,
                'project_category': project_category,
                'project_image': project_image,
                'project_categories': project_categories,  
                'skills': skills,  
            }

            valid, error_message = validate_form(project_name, project_description, project_image, project_budget, project_duration, skills_select, project_category)
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.new_project_template, context)
            
            client = Client.objects.get(user=request.user)
            
            project = Project.objects.create(
                title=project_name,
                description=project_description,
                budget=project_budget,
                status='draft' if action == 'draft' else 'processing',
                category=ProjectCategory.objects.get(id=project_category),
                deadline=project_duration,
                client=client,
            )
            
            if project_image:
                fs = FileSystemStorage(location='media/project_images')
                filename = fs.save(project_image.name, project_image)
                project.image = filename.split('/')[-1]
                
            project.skills.set(Skill.objects.filter(id__in=skills_select))  
            project.save()

            Notification.objects.create(
                user=request.user,
                message=f"Your project '{project.title}' has been successfully uploaded.",
            )                            

            messages.success(request, 'Your project has been added successfully.')
            return redirect(self.home_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.new_project_url)