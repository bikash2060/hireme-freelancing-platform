from django.urls import path
from .views import *

app_name = 'project'

urlpatterns = [
    path('add/', AddNewProjectView.as_view(), name='add-new-project'),
    path('<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail'),
]