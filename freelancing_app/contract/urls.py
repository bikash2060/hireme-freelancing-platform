from django.urls import path
from .views import *

app_name = 'contract'

urlpatterns = [
    path('client/contracts/', ClientContractListView.as_view(), name='client_contract_list'),
    path('client/contract/<int:contract_id>/', ClientContractDetailView.as_view(), name='client_contract_detail'),
    path('client/sign-contract/<int:contract_id>/', ClientSignContractView.as_view(), name='client_sign_contract'),
    path('client/complete-contract/<int:contract_id>/', ClientCompleteContractView.as_view(), name='client_complete_contract'),
    path('client/leave-review/<int:contract_id>/', ClientLeaveReviewView.as_view(), name='client_leave_review'),
    
    path('freelancer/contracts/', FreelancerContractListView.as_view(), name='freelancer_contract_list'),
    path('freelancer/contract/<int:contract_id>/', FreelancerContractDetailView.as_view(), name='freelancer_contract_detail'),
    path('freelancer/sign-contract/<int:contract_id>/', FreelancerSignContractView.as_view(), name='freelancer_sign_contract'),
]