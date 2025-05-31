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
from django.db.models import F

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
            
            # Get detailed active projects data with accepted proposals and contracts
            active_projects_data = active_projects.select_related(
                'category'
            ).prefetch_related(
                'proposals__freelancer__user',
                'proposals__contract'
            ).order_by('-created_at')[:6]
            
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

            # Performance metrics
            # 1. Project Spending
            current_month_spending = Contract.objects.filter(
                proposal__project__client=client,
                status='completed',
                end_date__month=datetime.now().month,
                end_date__year=datetime.now().year
            ).aggregate(total=Sum('agreed_amount'))['total'] or 0

            last_month_spending = Contract.objects.filter(
                proposal__project__client=client,
                status='completed',
                end_date__month=datetime.now().month - 1 if datetime.now().month > 1 else 12,
                end_date__year=datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
            ).aggregate(total=Sum('agreed_amount'))['total'] or 0

            spending_trend = ((current_month_spending - last_month_spending) / last_month_spending * 100) if last_month_spending else 0
            
            # Calculate spending percentage
            spending_percentage = (current_month_spending / total_spent * 100) if total_spent else 0
            spending_percentage = round(spending_percentage, 1)

            # 2. Active Projects
            planned_projects = 10  # This could be a setting or calculated based on client's history
            active_projects_trend = ((active_count - 5) / 5 * 100) if 5 > 0 else 0  # Assuming 5 was last month's count
            
            # Calculate active projects percentage
            active_projects_percentage = (active_count / planned_projects * 100) if planned_projects else 0
            active_projects_percentage = round(active_projects_percentage, 1)

            # 3. Freelancers Hired
            current_freelancers = Contract.objects.filter(
                proposal__project__client=client,
                status='active'
            ).values('proposal__freelancer').distinct().count()

            last_month_freelancers = Contract.objects.filter(
                proposal__project__client=client,
                status='active',
                start_date__month=datetime.now().month - 1 if datetime.now().month > 1 else 12,
                start_date__year=datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
            ).values('proposal__freelancer').distinct().count()

            freelancers_trend = ((current_freelancers - last_month_freelancers) / last_month_freelancers * 100) if last_month_freelancers else 0

            # 4. On-Time Completion
            total_completed = Contract.objects.filter(
                proposal__project__client=client,
                status='completed'
            ).count()

            # Calculate on-time completion based on contract end date and project's estimated duration
            on_time_completed = Contract.objects.filter(
                proposal__project__client=client,
                status='completed'
            ).annotate(
                days_taken=F('end_date') - F('start_date')
            ).filter(
                days_taken__lte=F('proposal__project__estimated_duration')
            ).count()

            on_time_percentage = (on_time_completed / total_completed * 100) if total_completed else 0
            on_time_percentage = round(on_time_percentage, 1)
            
            # Calculate on-time completion trend
            on_time_trend = on_time_percentage - 90  # Difference from target
            on_time_trend = round(on_time_trend, 1)

            # Monthly spending data for chart
            monthly_spending = Contract.objects.filter(
                proposal__project__client=client,
                status='completed',
                end_date__year=datetime.now().year
            ).values('end_date__month').annotate(
                total=Sum('agreed_amount')
            ).order_by('end_date__month')

            # Prepare chart data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            spending_data = [0] * 12
            for item in monthly_spending:
                spending_data[item['end_date__month'] - 1] = float(item['total'])

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
                'active_projects_data': active_projects_data,
                'total_projects': active_projects.count(),
                # Performance metrics
                'current_month_spending': current_month_spending,
                'last_month_spending': last_month_spending,
                'spending_trend': spending_trend,
                'spending_percentage': spending_percentage,
                'planned_projects': planned_projects,
                'active_projects_trend': active_projects_trend,
                'active_projects_percentage': active_projects_percentage,
                'current_freelancers': current_freelancers,
                'freelancers_trend': freelancers_trend,
                'on_time_percentage': on_time_percentage,
                'on_time_trend': on_time_trend,
                # Chart data
                'months': months,
                'spending_data': spending_data,
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
    