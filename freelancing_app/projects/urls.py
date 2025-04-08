from django.urls import path
from .views import *

app_name = 'project'

urlpatterns = [
   path('new/', NewProjectView.as_view(), name='new-project'),
]