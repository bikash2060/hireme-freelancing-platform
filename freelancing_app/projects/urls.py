from django.urls import path
from .views import *

app_name = 'project'

urlpatterns = [
   path('new/', NewProjectView.as_view(), name='new-project'),
   path('my-projects/', ClientProjectsView.as_view(), name='client-projects'),
   path('my-projects/<int:project_id>/details/', ClientProjectDetailView.as_view(), name='client-project-detail'),
   path('my-projects/<int:project_id>/publish/', PublishProjectView.as_view(), name='publish-project'),
   path('my-projects/<int:project_id>/update/', EditProjectView.as_view(), name='edit-project'),
   path('my-projects/<int:project_id>/delete/', DeleteProjectView.as_view(), name='delete-project'),
   path('my-projects/<int:project_id>/set-hiring/', SetHiringView.as_view(), name='set-hiring'),
   path('my-projects/<int:project_id>/proposals/', ProjectProposalsView.as_view(), name='project-proposals'),
   path('my-projects/<int:project_id>/proposals/<int:proposal_id>/details/', ProjectProposalDetailsView.as_view(), name='project-proposal-details'),
   path('my-projects/<int:project_id>/proposals/<int:proposal_id>/<str:action>/', ProposalActionView.as_view(), name='proposal-action'),
]