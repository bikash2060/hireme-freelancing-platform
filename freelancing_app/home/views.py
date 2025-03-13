from django.shortcuts import render, redirect
from django.views import View
from projects.models import Skill
from accounts.mixins import CustomLoginRequiredMixin
from .models import Notification    
from django.contrib import messages
from django.contrib.auth import logout
from projects.models import Project
from accounts.models import Freelancer
from django.utils.timezone import now

# Testing In-Progress
class MarkAllAsReadView(CustomLoginRequiredMixin, View):
    
    def get(self, request):
        try:
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
            unread_notifications.update(is_read=True)
            return redirect('homes:home')  
        except Exception as e:
            return redirect('homes:home')  
        
# Testing In-Progress
class HomeView(View):
    freelancer_dashboard_url = 'dashboard:freelancer'
    client_dashboard_url = 'dashboard:client'
    home_template = 'home/index.html'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                user_role = request.user.role.lower()  
                
                if user_role == 'client':
                    return redirect(self.client_dashboard_url)
                else:
                    return redirect(self.freelancer_dashboard_url)
                
            freelancer_count = Freelancer.objects.count()
            project_count = Project.objects.count()     
            projects = Project.objects.exclude(status='draft').order_by('-created_at')
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            logout(request)
            return render(request, self.home_template)
        
        current_year = now().year
        context = {
            'freelancer_count': freelancer_count,
            'project_count': project_count,
            'projects': projects,
            'completed_projects': 0,  
            'positive_reviews': 0,  
            'current_year': current_year,
        }
        return render(request, self.home_template, context)

# Testing In-Progress
class GetUserProfileView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    client_profile_url = 'client:profile'
    home_url = 'homes:home'
    
    def get(self, request):
        user_role = request.user.role 
        
        if user_role.lower() == 'client':
            return redirect(self.client_profile_url)
        else:
            return redirect(self.freelancer_profile_url)

# Testing In-Progress
def handling_404(request, exception):
    return render(request, '404.html', {})

# Testing In-Progress
class FreelancersView(View):
    
    rendered_template = 'home/freelancers.html'
    
    def get(self, request):
        skills = Skill.objects.all().order_by('name')
        
        context = {
            'skills': skills
        }
        return render(request, self.rendered_template, context)

# Testing In-Progress
class ProjectsView(View):
    
    rendered_template = 'home/projects.html'
    
    def get(self, request):
        return render(request, self.rendered_template)