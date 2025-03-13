from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime
from accounts.mixins import CustomLoginRequiredMixin
from projects.models import Project
from accounts.models import Client, Freelancer
from .models import Proposal
from home.models import Notification
from django.db.models import Count

class ClientDashboardView(CustomLoginRequiredMixin, View):
    
    rendered_template = 'dashboard/clientdashboard.html'
    
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        client = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=client).annotate(num_proposals=Count('proposals'))

        context = {
            'greeting': greeting,
            'projects': projects,
        }
        return render(request, self.rendered_template, context)
    
class FreelancerDashboardView(CustomLoginRequiredMixin, View):
    
    rendered_template = 'dashboard/freelancerdashboard.html'
        
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        freelancer = Freelancer.objects.get(user=request.user)
        projects = Project.objects.exclude(status='draft').order_by('-created_at')
        context = {
            'greeting': greeting,
            'projects': projects,
            'freelancer': freelancer
        }
        
        return render(request, self.rendered_template, context)
    
class NewProposalsView(CustomLoginRequiredMixin, View):
    rendered_template = 'proposals/proposals_form.html'
    
    def get(self, request, proposal_id):
        project = Project.objects.get(id=proposal_id)  
        return render(request, self.rendered_template, {'project': project})
    
    def post(self, request, proposal_id):
        project = Project.objects.get(id=proposal_id)

        proposal_description = request.POST.get('proposal-description')
        bid_amount = request.POST.get('bid-amount')
        estimated_delivery_time = request.POST.get('estimated-delivery-time')

        if not proposal_description or not bid_amount or not estimated_delivery_time:
            messages.error(request, "All fields are required!")
            return render(request, self.rendered_template, {
                'project': project,
                'proposal_description': proposal_description,
                'bid_amount': bid_amount,
                'estimated_delivery_time': estimated_delivery_time,
            })

        freelancer = Freelancer.objects.get(user=request.user)  
        proposal = Proposal(
            project=project,
            freelancer=freelancer,
            proposal_description=proposal_description,
            bid_amount=bid_amount,
            estimated_delivery_time=estimated_delivery_time,
        )
        Notification.objects.create(
            user=project.client.user,
            message=f"You have received a new proposal for your project {project.title} from {freelancer.user.username}"
        )
        proposal.save()

        messages.success(request, "Your proposal has been submitted successfully!")
        return redirect('dashboard:freelancer')  



    