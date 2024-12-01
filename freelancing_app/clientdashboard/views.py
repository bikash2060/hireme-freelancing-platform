from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def show_dashboard(request):
    user = request.user  
    context = {
        'user': user,
    }
    print("Usename", user.username)
    return render(request, "dashboard/clientdashboard.html", context)