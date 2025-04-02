from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render
from clientprofile.models import Client
from django.db.models import Count
from django.views import View
from datetime import datetime

class ClientDashboardView(CustomLoginRequiredMixin, View):
    
    rendered_template = 'dashboard/clientdashboard.html'
    
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        client = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=client).annotate(num_proposals=Count('proposals'))

        context = {
            'greeting': greeting,
            'projects': projects,
        }
        return render(request, self.rendered_template, context)
    
class FreelancerDashboardView(CustomLoginRequiredMixin, View):
    
    freelancer_dashboard_template = 'dashboard/freelancerdashboard.html'
        
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 18:
            greeting = "Good Afternoon"
        elif 18 <= current_hour < 21:
            greeting = "Good Evening"
        else:
            greeting = "Good Night"

        freelancer = Freelancer.objects.get(user=request.user)
        projects = Project.objects.exclude(status='draft').order_by('-created_at')
        context = {
            'greeting': greeting,
            'projects': projects,
            'freelancer': freelancer
        }
        return render(request, self.freelancer_dashboard_template, context)
    