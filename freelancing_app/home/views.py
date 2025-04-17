from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from clientprofile.models import Client
from django.contrib.auth import logout
from django.utils.timezone import now
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator
from projects.models import ProjectCategory, Skill, Project
from django.db.models import Q

class HomeView(View):
    freelancer_dashboard_url = 'dashboard:freelancer'
    client_dashboard_url = 'dashboard:client'
    home_template = 'home/index.html'
    
    def get(self, request):
        try:
            if request.user.is_authenticated:
                user_role = request.user.role.lower()  
                
                if user_role == 'client':
                    try:
                        client = Client.objects.get(user=request.user)
                        return redirect(self.client_dashboard_url)
                    except Client.DoesNotExist:
                        messages.error(request, 'No client profile found for this account.')
                        logout(request)
                        return render(request, self.home_template)
                
                elif user_role == 'freelancer':
                    try:
                        freelancer = Freelancer.objects.get(user=request.user)
                        return redirect(self.freelancer_dashboard_url)
                    except Freelancer.DoesNotExist:
                        messages.error(request, 'No freelancer profile found for this account.')
                        logout(request)
                        return render(request, self.home_template)
                
                else:
                    messages.error(request, 'Invalid user role. Please try again.')
                    logout(request)
                    return render(request, self.home_template)
        
            freelancer_count = Freelancer.objects.count() or 0
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            logout(request)
            return render(request, self.home_template)
        
        current_year = now().year
        context = {
            'freelancer_count': freelancer_count,
            'project_count': 0,
            'projects': 0,
            'completed_projects': 0,  
            'positive_reviews': 0,  
            'current_year': current_year,
        }
        return render(request, self.home_template, context)

class GetUserProfileView(CustomLoginRequiredMixin, View):
    home_template = 'home/index.html'
    freelancer_profile_url = 'freelancer:profile'
    client_profile_url = 'client:profile'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            user_role = request.user.role 
            
            if user_role.lower() == 'client':
                return redirect(self.client_profile_url)
            elif user_role.lower() == 'freelancer':
                return redirect(self.freelancer_profile_url)
            else:
                messages.error(request, 'Something went wrong. Please try again.')
                logout(request)
                return render(request, self.home_template)
        
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)
        
class UserSpecificProjectListView(View):
    client_project_list_url = 'project:client-projects'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            user_role = request.user.role
            
            if user_role.lower() == 'client':
                return redirect(self.client_project_list_url)
            else:
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect(self.home_url)
        except Exception:   
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)

class FreelancerListView(View):
    freelancer_list_template = 'home/freelancerslist.html'
    home_url = 'home:home' 

    def get(self, request):
        if self.has_access(request.user):
            return render(request, self.freelancer_list_template, {})
        return redirect(self.home_url)
    
    def has_access(self, user):
        """Strict access: Only unauthenticated or clients can view."""
        if not user.is_authenticated:
            return True
        return getattr(user, 'role', None) == 'client' 
    
class ProjectListView(View):
    project_list_template = 'home/projectlist.html'
    home_url = 'home:home' 
    items_per_page = 10

    def get(self, request):
        if self.has_access(request.user):
            categories = ProjectCategory.objects.all()
            skills = Skill.objects.all()
            projects = Project.objects.filter(
                status=Project.Status.PUBLISHED
            ).distinct().order_by('-created_at')
                        
            selected_categories = request.GET.getlist('category')
            selected_experience = request.GET.getlist('experience')
            selected_budgets = request.GET.getlist('budget')
            selected_durations = request.GET.getlist('duration')
            selected_skills = request.GET.getlist('skill')
            
            keyword = request.GET.get('search')
            
            if keyword:
                projects = projects.filter(
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(category__name__icontains=keyword) |
                    Q(skills_required__name__icontains=keyword)
                ).distinct()
            
            if selected_categories and 'all' not in selected_categories:
                projects = projects.filter(category_id__in=selected_categories)
                
            if selected_experience and 'all' not in selected_experience:
                projects = projects.filter(experience_level__in=selected_experience)
                
            if selected_budgets and 'all' not in selected_budgets:
                budget_q = Q()
                for b in selected_budgets:
                    if b == '500000+':
                        budget_q |= Q(fixed_budget__gte=500000) | Q(budget_max__gte=500000)
                    else:
                        parts = b.split('-')
                        if len(parts) == 2:
                            min_val, max_val = map(int, parts)
                            budget_q |= (
                                Q(fixed_budget__gte=min_val, fixed_budget__lte=max_val) |
                                Q(budget_min__gte=min_val, budget_max__lte=max_val)
                            )
                projects = projects.filter(budget_q)
                
            if selected_durations and 'all' not in selected_durations:
                duration_q = Q()
                for d in selected_durations:
                    if d == '12+':
                        duration_q |= Q(estimated_duration__gte=12)
                    else:
                        min_d, max_d = map(int, d.split('-'))
                        duration_q |= Q(estimated_duration__gte=min_d, estimated_duration__lte=max_d)
                projects = projects.filter(duration_q)
                
            if selected_skills and 'all' not in selected_skills:
                projects = projects.filter(skills_required__id__in=selected_skills).distinct()
                
            paginator = Paginator(projects, self.items_per_page)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            categories_dict = {str(c.id): c for c in categories}
            skills_dict = {str(s.id): s for s in skills}
            
            context = {
                'projects': page_obj,
                'categories': categories,
                'skills': skills,
                'expertise_levels': Project.ExpertiseLevel.choices,
                'selected_categories': selected_categories,
                'selected_experience': selected_experience,
                'selected_budgets': selected_budgets,
                'selected_durations': selected_durations,
                'selected_skills': selected_skills,  
                'search_keyword': keyword,
                'categories_dict': categories_dict,
                'skills_dict': skills_dict,
            }
            
            return render(request, self.project_list_template, context)
        return redirect(self.home_url)
    
    def has_access(self, user):
        """Strict access: Only unauthenticated or freelancers can view."""
        if not user.is_authenticated:
            return True
        return getattr(user, 'role', None) == 'freelancer' 
    
class ProjectDetailView(View):
    template_name = 'home/project-detail.html'
    home_url = 'home:home'
    
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, status=Project.Status.PUBLISHED)
            
            if request.user.is_authenticated:
                if request.user.role.lower() == 'client' and project.client.user != request.user:
                    return redirect(self.home_url)
            
            context = {
                'project': project,
            }
            return render(request, self.template_name, context)
            
        except Project.DoesNotExist:
            messages.error(request, "Project not found or no longer available")
            return redirect(self.home_url)
        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong. Please try again.")
            return redirect(self.home_url)

def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})
