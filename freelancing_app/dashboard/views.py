from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from clientprofile.models import Client
from django.db.models import Count, Sum, Avg
from django.views import View
from datetime import datetime, timedelta
from django.contrib import messages
from projects.models import Project
from proposals.models import Proposal
from contract.models import Contract, Review, Transaction
from django.db.models import Q
from django.db.models import F
from django.db.models import Avg as AvgModel
from django.db.models.functions import ExtractMonth

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
            
            active_projects = Project.objects.filter(client=client, status__in=['in_progress', 'hiring'])
            active_count = active_projects.count()
            in_development = active_projects.filter(status='in_progress').count()
            in_review = active_projects.filter(status='hiring').count()
            
            # Get only in_progress projects for the active projects section
            active_projects_data = Project.objects.filter(
                client=client, 
                status='in_progress'
            ).select_related(
                'category'
            ).prefetch_related(
                'proposals__freelancer__user',
                'proposals__contract'
            ).order_by('-created_at')[:6]
            
            new_proposals = Proposal.objects.filter(
                project__client=client,
                status='pending'
            ).count()
            
            shortlisted_proposals = Proposal.objects.filter(
                project__client=client,
                is_shortlisted=True
            ).count()
            
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
            
            completed_projects = Project.objects.filter(
                client=client,
                status='completed'
            )
            completed_count = completed_projects.count()

            # Performance metrics
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
            
            spending_percentage = (current_month_spending / total_spent * 100) if total_spent else 0
            spending_percentage = round(spending_percentage, 1)

            planned_projects = 10 
            active_projects_trend = ((active_count - 5) / 5 * 100) if 5 > 0 else 0 
            
            active_projects_percentage = (active_count / planned_projects * 100) if planned_projects else 0
            active_projects_percentage = round(active_projects_percentage, 1)

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

            total_completed = Contract.objects.filter(
                proposal__project__client=client,
                status='completed'
            ).count()

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
            
            on_time_trend = on_time_percentage - 90  
            on_time_trend = round(on_time_trend, 1)

            monthly_spending = Contract.objects.filter(
                proposal__project__client=client,
                status='completed',
                end_date__year=datetime.now().year
            ).values('end_date__month').annotate(
                total=Sum('agreed_amount')
            ).order_by('end_date__month')

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
        
        # Get work performance stats
        completed_contracts = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed'
        )
        total_completed = completed_contracts.count()
        
        # Calculate average rating from completed projects
        reviews = Review.objects.filter(
            contract__proposal__freelancer=freelancer,
            reviewer_type='client'
        )
        average_rating = reviews.aggregate(avg_rating=AvgModel('rating'))['avg_rating'] or 0
        
        # Get current workload stats
        active_contracts = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='active'
        )
        active_count = active_contracts.count()
        
        # Get contracts ending this week
        today = datetime.now().date()
        end_of_week = today + timedelta(days=(6 - today.weekday()))  # Get end of current week (Sunday)
        start_of_week = end_of_week - timedelta(days=6)  # Get start of current week (Monday)
        
        contracts_ending_this_week = active_contracts.filter(
            end_date__gte=start_of_week,
            end_date__lte=end_of_week
        ).count()
        
        # Get upcoming deadlines (next 7 days)
        next_week = today + timedelta(days=7)
        upcoming_contracts = active_contracts.filter(
            end_date__gte=today,
            end_date__lte=next_week
        ).select_related(
            'proposal__project__client__user'
        ).order_by('end_date')[:3]
        
        # Get proposal success rate
        total_proposals = Proposal.objects.filter(freelancer=freelancer).count()
        accepted_proposals = Proposal.objects.filter(
            freelancer=freelancer,
            status='accepted'
        ).count()
        success_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0
        
        # Get earnings stats
        total_earnings = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed'
        ).aggregate(total=Sum('agreed_amount'))['total'] or 0
        
        # Get all completed contracts for the freelancer in the current year
        completed_contracts = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed',
            completed_date__year=datetime.now().year
        )

        # Group by month and sum the agreed_amount
        monthly_earnings = completed_contracts.annotate(
            month=ExtractMonth('completed_date')
        ).values('month').annotate(
            total=Sum('agreed_amount')
        ).order_by('month')

        # Prepare data for all 12 months
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        earnings_data = [0] * 12
        for item in monthly_earnings:
            if item['month']:
                earnings_data[item['month'] - 1] = float(item['total'])

        # Calculate current month earnings
        current_month_earnings = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed',
            completed_date__month=datetime.now().month,
            completed_date__year=datetime.now().year
        ).aggregate(total=Sum('agreed_amount'))['total'] or 0

        # Calculate last month earnings
        last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
        last_month_year = datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
        last_month_earnings = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed',
            completed_date__month=last_month,
            completed_date__year=last_month_year
        ).aggregate(total=Sum('agreed_amount'))['total'] or 0

        # Calculate earnings growth
        earnings_growth = ((current_month_earnings - last_month_earnings) / last_month_earnings * 100) if last_month_earnings else 0

        # Performance metrics for dashboard
        # 1. Earnings target (based on last 3 months average)
        last_3_months_earnings = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed',
            completed_date__gte=datetime.now().date() - timedelta(days=90)
        ).aggregate(total=Sum('agreed_amount'))['total'] or 0
        
        earnings_target = (last_3_months_earnings / 3) if last_3_months_earnings else 0
        earnings_percentage = (current_month_earnings / earnings_target * 100) if earnings_target else 0
        earnings_percentage = min(earnings_percentage, 100)  # Cap at 100%

        # 2. Projects target (based on last 3 months average)
        last_3_months_projects = Contract.objects.filter(
            proposal__freelancer=freelancer,
            status='completed',
            completed_date__gte=datetime.now().date() - timedelta(days=90)
        ).count()
        
        projects_target = (last_3_months_projects / 3) if last_3_months_projects else 0
        projects_percentage = (active_count / projects_target * 100) if projects_target else 0
        projects_percentage = min(projects_percentage, 100)  # Cap at 100%

        # 3. Client satisfaction (based on ratings)
        rating_target = 5.0  # Maximum possible rating
        rating_percentage = (average_rating / rating_target * 100) if rating_target else 0
        rating_percentage = min(rating_percentage, 100)  # Cap at 100%

        # 4. On-time delivery rate
        on_time_deliveries = completed_contracts.filter(
            completed_date__lte=F('end_date')
        ).count()
        on_time_percentage = (on_time_deliveries / total_completed * 100) if total_completed else 0

        client_reviews = Review.objects.filter(
            contract__proposal__freelancer=freelancer,
            reviewer_type=Review.ReviewerType.CLIENT
        ).select_related('contract__proposal__project__client__user').order_by('-created_at')[:10]

        context = {
            'greeting': greeting,
            'freelancer': freelancer,
            'average_rating': round(average_rating, 1),
            'total_completed': total_completed,
            'active_contracts': active_count,
            'contracts_ending_this_week': contracts_ending_this_week,
            'success_rate': round(success_rate, 1),
            'accepted_proposals': accepted_proposals,
            'total_earnings': total_earnings,
            'earnings_growth': round(earnings_growth, 1),
            'upcoming_contracts': upcoming_contracts,
            # Performance dashboard data
            'current_month_earnings': current_month_earnings,
            'earnings_target': earnings_target,
            'earnings_percentage': round(earnings_percentage, 1),
            'projects_target': round(projects_target, 1),
            'projects_percentage': round(projects_percentage, 1),
            'rating_target': rating_target,
            'rating_percentage': round(rating_percentage, 1),
            'on_time_percentage': round(on_time_percentage, 1),
            'months': months,
            'earnings_data': earnings_data,
            'client_reviews': client_reviews,
        }
        return render(request, self.freelancer_dashboard_template, context)
    