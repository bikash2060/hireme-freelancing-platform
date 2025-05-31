from django.urls import path
from . import views

app_name = 'contract'

urlpatterns = [
    # Contract list views
    path('client/contracts/', views.ClientContractListView.as_view(), name='client_contract_list'),
    path('freelancer/contracts/', views.FreelancerContractListView.as_view(), name='freelancer_contract_list'),
    
    # Contract detail views
    path('client/contract/<int:contract_id>/', views.ClientContractDetailView.as_view(), name='client_contract_detail'),
    path('freelancer/contract/<int:contract_id>/', views.FreelancerContractDetailView.as_view(), name='freelancer_contract_detail'),
    
    # Contract signing views
    path('client/contract/<int:contract_id>/sign/', views.ClientSignContractView.as_view(), name='client_sign_contract'),
    path('freelancer/contract/<int:contract_id>/sign/', views.FreelancerSignContractView.as_view(), name='freelancer_sign_contract'),
    
    # Workspace views
    path('workspace/<int:contract_id>/', views.WorkspaceView.as_view(), name='workspace'),
    path('workspace/<int:contract_id>/submit-work/', views.CreateSubmissionView.as_view(), name='submit_work'),
    path('workspace/<int:contract_id>/submit-final-work/<int:submission_id>/', views.SubmitFinalWorkView.as_view(), name='submit_final_work'),
    path('workspace/<int:contract_id>/review-submission/<int:submission_id>/', views.ReviewSubmissionView.as_view(), name='review_submission'),
    path('workspace/<int:contract_id>/process-payment/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('workspace/<int:contract_id>/leave-review/', views.LeaveReviewView.as_view(), name='leave_review'),
]