from django.shortcuts import render, redirect
from django.views import View
from accounts.mixins import CustomLoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import Project
from .utils import *
from accounts.models import Client

class AddNewProjectView(CustomLoginRequiredMixin, View):
    
    rendered_template = 'projects/addproject.html'
    
    redirected_URL = 'project:add-new-project'
    
    def get(self, request):
        return render(request, self.rendered_template)
        
    def post(self, request):
        project_name = request.POST.get('project-name').strip()
        project_description = request.POST.get('project-description')
        project_image = request.FILES.get('project-image')  
        project_budget = request.POST.get('project-budget')
        project_duration = request.POST.get('project-duration')
        skills_select = request.POST.getlist('skills-select')  
        project_category = request.POST.get('project-category')
        
        action = request.POST.get('action')  # "submit" or "draft"
        
        context = {
            'project_name': project_name,
            'project_description': project_description,
            'project_budget': project_budget,
            'project_duration': project_duration,
            'skills_select': skills_select,
            'project_category': project_category,
            'project_image': project_image
        }

        valid, error_message = validate_form(project_name, project_description, project_image, project_budget, project_duration, skills_select, project_category)
        
        if not valid:
            messages.error(request, error_message)
            return render(request, self.rendered_template, context)
        
        try:
            client = Client.objects.get(user=request.user)
            
            project = Project.objects.create(
                title=project_name,
                description=project_description,
                budget=project_budget,
                category=project_category,
                deadline=project_duration,
                client=client,
                status='draft' if action == 'draft' else 'processing'  
            )
            
            if project_image:
                fs = FileSystemStorage(location='media/project_images')
                filename = fs.save(project_image.name, project_image)
                project.image = filename.split('/')[-1]
                
            project.save()
            
            messages.success(request, "New project added successfully.")
            return redirect(self.redirected_URL)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, self.rendered_template, context)
