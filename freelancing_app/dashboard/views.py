from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from clientprofile.models import Client
from django.db.models import Count, Sum, Avg
from django.views import View
from datetime import datetime
from django.contrib import messages
from projects.models import Project
from proposals.models import Proposal
from contract.models import Contract
from django.db.models import Q

class ClientDashboardView(CustomLoginRequiredMixin, View):
    
    rendered_template = 'dashboard/clientdashboard.html'
    
    def get(self, request):
        try:
            current_hour = datetime.now().hour

            if 0 <= current_hour < 12:
                greeting = "Good Morning"
            elif 12 <= current_hour < 18:
                greeting = "Good Afternoon"
            elif 18 <= current_hour < 21:
                greeting = "Good Evening"
            else:
                greeting = "Good Night"

            client = Client.objects.get(user=request.user)
            
            # Get active projects count
            active_projects = Project.objects.filter(client=client, status__in=['in_progress', 'hiring'])
            active_count = active_projects.count()
            in_development = active_projects.filter(status='in_progress').count()
            in_review = active_projects.filter(status='hiring').count()
            
            # Get proposals count
            new_proposals = Proposal.objects.filter(
                project__client=client,
                status='pending'
            ).count()
            
            shortlisted_proposals = Proposal.objects.filter(
                project__client=client,
                is_shortlisted=True
            ).count()
            
            # Get financial data
            total_spent = Contract.objects.filter(
                proposal__project__client=client,
                status='completed'
            ).aggregate(
                total=Sum('agreed_amount')
            )['total'] or 0
            
            pending_payments = Contract.objects.filter(
                proposal__project__client=client,
                status='active'
            ).aggregate(
                total=Sum('agreed_amount')
            )['total'] or 0
            
            # Get work quality data
            completed_projects = Project.objects.filter(
                client=client,
                status='completed'
            )
            completed_count = completed_projects.count()

            context = {
                'client': client,
                'greeting': greeting,
                'active_projects': active_count,
                'in_development': in_development,
                'in_review': in_review,
                'new_proposals': new_proposals,
                'shortlisted_proposals': shortlisted_proposals,
                'total_spent': total_spent,
                'pending_payments': pending_payments,
                'completed_projects': completed_count,
            }
            return render(request, self.rendered_template, context)
            
        except Client.DoesNotExist:
            messages.error(request, "Client profile not found. Please complete your profile setup.")
            return redirect('clientprofile:create')
        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong. Please try again later.")
            return render(request, self.rendered_template, {'greeting': greeting})
    
class FreelancerDashboardView(CustomLoginRequiredMixin, View):
    
    freelancer_dashboard_template = 'dashboard/freelancerdashboard.html'
        
    def get(self, request):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 18:
            greeting = "Good Afternoon"
        elif 18 <= current_hour < 21:
            greeting = "Good Evening"
        else:
            greeting = "Good Night"

        freelancer = Freelancer.objects.get(user=request.user)
        context = {
            'greeting': greeting,
            'freelancer': freelancer
        }
        return render(request, self.freelancer_dashboard_template, context)
    