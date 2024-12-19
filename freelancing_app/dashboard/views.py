from django.views import View
from django.shortcuts import render, redirect, HttpResponse

class ClientDashboardView(View):
    
    def get(self, request):
        return render(request, 'dashboard/clientdashboard.html')
    
class FreelancerDashboardView(View):
    
    def get(self, request):
        return HttpResponse('freelancer/dashboard')