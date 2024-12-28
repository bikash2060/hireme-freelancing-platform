from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse

class HomeView(View):
    
     # Handle GET requests to render the home page.
    def get(self, request):
        if request.user.is_authenticated:
            user_role = request.user.role 
            
            # Redirect based on the user's role
            if user_role == 'client':
                return redirect('dashboard:client')
            elif user_role == 'freelancer':
                return redirect('freelancer_dashboard')
        
        # Render the default home page if the user is not authenticated
        return render(request, 'home/index.html')

def handling_404(request, exception):
    return render(request, '404.html', {})