from django.urls import path
from .views import *

app_name = 'contract'

urlpatterns = [
    path('create/<int:proposal_id>/', CreateContractView.as_view(), name='create-contract'),
    path('client/<int:contract_id>/', ClientContractDetailView.as_view(), name='client-contract-detail'),
    path('freelancer/<int:contract_id>/', FreelancerContractDetailView.as_view(), name='freelancer-contract-detail'),
    path('sign/<int:contract_id>/', SignContractView.as_view(), name='sign-contract'),
    path('submit-work/<int:contract_id>/', SubmitWorkView.as_view(), name='submit-work'),
    path('review-work/<int:submission_id>/<str:action>/', ReviewWorkView.as_view(), name='review-work'),
    path('process-payment/<int:contract_id>/', ProcessPaymentView.as_view(), name='process-payment'),
    path('submit-review/<int:contract_id>/', SubmitReviewView.as_view(), name='submit-review'),
]