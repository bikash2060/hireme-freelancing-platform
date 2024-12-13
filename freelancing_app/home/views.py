from django.shortcuts import render
from django.views import View

class HomeView(View):
    
    # Handle GET requests to render the home page.
    def get(self, request):
        return render(request, 'home/index.html')
