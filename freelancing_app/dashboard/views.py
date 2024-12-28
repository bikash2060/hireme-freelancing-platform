from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from accounts.mixins import CustomLoginRequiredMixin
from projects.models import Project
from accounts.models import Client

class ClientDashboardView(CustomLoginRequiredMixin, View):
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        client = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=client)

        context = {
            'greeting': greeting,
            'projects': projects,  
        }
        return render(request, 'dashboard/clientdashboard.html', context)
    
class FreelancerDashboardView(View):
    
    def get(self, request):
        return HttpResponse('freelancer/dashboard')