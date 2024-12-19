from django.shortcuts import render
from django.views import View

class ClientDashboardView(View):
    rendered_template = 'dashboard/clientdashboard.html'
    
    def get(self, request):
        return render(request, self.rendered_template)        