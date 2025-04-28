from django.urls import path
from .views import *

app_name = 'proposal'

urlpatterns = [
    path('<int:project_id>/apply/', SubmitProposalView.as_view(), name='submit-proposal'),
    path('my-proposals/', FreelancerProposalsView.as_view(), name='freelancer-proposals'),
    path('<int:proposal_id>/details/', FreelancerProposalDetailView.as_view(), name='freelancer-proposal-detail'),
    path('<int:proposal_id>/edit/', EditProposalView.as_view(), name='edit-proposal'),
    path('<int:proposal_id>/delete/', DeleteProposalView.as_view(), name='delete-proposal'),
]
