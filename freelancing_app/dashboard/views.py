from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime

class ClientDashboardView(View):
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        context = {
            'greeting': greeting,
        }
        return render(request, 'dashboard/clientdashboard.html', context)
    
class FreelancerDashboardView(View):
    
    def get(self, request):
        return HttpResponse('freelancer/dashboard')