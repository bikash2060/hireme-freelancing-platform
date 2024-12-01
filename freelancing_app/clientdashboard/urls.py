from django.urls import path
from . import views

app_name = 'clientdashboard'  

urlpatterns = [
    path("client/", views.show_dashboard, name="dashboard"),
    
]