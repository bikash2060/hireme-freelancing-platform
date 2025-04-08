from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from clientprofile.models import Client
from django.contrib.auth import logout
from django.utils.timezone import now
from django.contrib import messages
from .models import Notification    
from django.views import View

class HomeView(View):
    freelancer_dashboard_url = 'dashboard:freelancer'
    client_dashboard_url = 'dashboard:client'
    home_template = 'home/index.html'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                user_role = request.user.role.lower()  
                
                if user_role == 'client':
                    try:
                        client = Client.objects.get(user=request.user)
                        return redirect(self.client_dashboard_url)
                    except Client.DoesNotExist:
                        messages.error(request, 'No client profile found for this account.')
                        logout(request)
                        return render(request, self.home_template)
                
                elif user_role == 'freelancer':
                    try:
                        freelancer = Freelancer.objects.get(user=request.user)
                        return redirect(self.freelancer_dashboard_url)
                    except Freelancer.DoesNotExist:
                        messages.error(request, 'No freelancer profile found for this account.')
                        logout(request)
                        return render(request, self.home_template)
                
                else:
                    messages.error(request, 'Invalid user role. Please try again.')
                    logout(request)
                    return render(request, self.home_template)
        
            freelancer_count = Freelancer.objects.count() or 0
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            logout(request)
            return render(request, self.home_template)
        
        current_year = now().year
        context = {
            'freelancer_count': freelancer_count,
            'project_count': 0,
            'projects': 0,
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
    home_template = 'home/index.html'
    freelancer_profile_url = 'freelancer:profile'
    client_profile_url = 'client:profile'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            user_role = request.user.role 
            
            if user_role.lower() == 'client':
                return redirect(self.client_profile_url)
            elif user_role.lower() == 'freelancer':
                return redirect(self.freelancer_profile_url)
            else:
                messages.error(request, 'Something went wrong. Please try again.')
                logout(request)
                return render(request, self.home_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})
