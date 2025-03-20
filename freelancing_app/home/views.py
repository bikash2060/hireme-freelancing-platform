from django.shortcuts import render, redirect
from django.views import View
from accounts.mixins import CustomLoginRequiredMixin
from .models import Notification    
from django.contrib import messages
from django.contrib.auth import logout
from projects.models import Project
from accounts.models import Freelancer
from django.utils.timezone import now

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

class MarkAllAsReadView(CustomLoginRequiredMixin, View):
    home_url = 'home:home'
    
    def get(self, request):
        try:
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
            unread_notifications.update(is_read=True)
            return redirect(self.home_url)  
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)  

class GetUserProfileView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    client_profile_url = 'client:profile'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            user_role = request.user.role 
            
            if user_role.lower() == 'client':
                return redirect(self.client_profile_url)
            else:
                return redirect(self.freelancer_profile_url)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})
