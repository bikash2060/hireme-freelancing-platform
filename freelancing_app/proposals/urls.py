from django.urls import path
from .views import *

app_name = 'proposal'

urlpatterns = [
    path('<int:project_id>/apply/', SubmitProposalView.as_view(), name='submit-proposal'),
]
