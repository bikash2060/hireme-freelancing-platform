from django.shortcuts import render, redirect
from django.views import View
from projects.models import Skill
from accounts.mixins import CustomLoginRequiredMixin
from .models import Notification    


class MarkAllAsReadView(CustomLoginRequiredMixin, View):
    
    def get(self, request):
        try:
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
            unread_notifications.update(is_read=True)
            return redirect('homes:home')  
        except Exception as e:
            return redirect('homes:home')  
        

class HomeView(View):
    
    def get(self, request):
        if request.user.is_authenticated:
            user_role = request.user.role 
            
            if user_role == 'client':
                return redirect('dashboard:client')
            elif user_role == 'freelancer':
                return redirect('dashboard:freelancer')
        
        return render(request, 'home/index.html')

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

def handling_404(request, exception):
    return render(request, '404.html', {})

class FreelancersView(View):
    
    rendered_template = 'home/freelancers.html'
    
    def get(self, request):
        skills = Skill.objects.all().order_by('name')
        
        context = {
            'skills': skills
        }
        return render(request, self.rendered_template, context)
    
class ProjectsView(View):
    
    rendered_template = 'home/projects.html'
    
    def get(self, request):
        return render(request, self.rendered_template)