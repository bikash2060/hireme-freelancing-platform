from projects.models import ProjectCategory, Skill, Project
from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from clientprofile.models import Client
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.views import View

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: HomeView
# Description: Handles routing for authenticated and unauthenticated users
# Tested On: 2025-04-18
# Status: Working as expected
# ------------------------------------------------------
class HomeView(View):
    """
    - Redirecting authenticated users to appropriate dashboards based on their role
    - Handling cases where user profiles are missing
    - Displaying the homepage for unauthenticated users
    - Managing error cases and logout scenarios
    """
    
    # URL constants for redirection
    FREELANCER_DASHBOARD_URL = 'dashboard:freelancer'
    CLIENT_DASHBOARD_URL = 'dashboard:client'
    TEMPLATE_NAME = 'home/index.html'  
    
    def get(self, request):
        """
        Main entry point for GET requests.
        Routes authenticated users to appropriate handlers or renders homepage.
        """
        if request.user.is_authenticated:
            return self._handle_authenticated_user(request)
        return self._render_home_page(request)

    def _handle_authenticated_user(self, request):
        """
        Handles routing for authenticated users based on their role.
        Uses dictionary dispatch pattern for role-based handling.
        """
        user_role = request.user.role.lower()
        
        role_handlers = {
            'client': self._handle_client,
            'freelancer': self._handle_freelancer,
        }
        
        handler = role_handlers.get(user_role, self._handle_invalid_role)
        return handler(request)

    def _handle_client(self, request):
        """
        Handles client users:
        - Verifies client profile exists
        - Redirects to client dashboard if profile exists
        - Handles missing profile case
        """
        try:
            Client.objects.get(user=request.user)
            return redirect(self.CLIENT_DASHBOARD_URL)
        except Client.DoesNotExist:
            return self._handle_missing_profile(request, 'client')

    def _handle_freelancer(self, request):
        """
        Handles freelancer users:
        - Verifies freelancer profile exists
        - Redirects to freelancer dashboard if profile exists
        - Handles missing profile case
        """
        try:
            Freelancer.objects.get(user=request.user)
            return redirect(self.FREELANCER_DASHBOARD_URL)
        except Freelancer.DoesNotExist:
            return self._handle_missing_profile(request, 'freelancer')

    def _handle_invalid_role(self, request):
        """
        Handles cases where user has an unrecognized role.
        Logs out user and shows error message.
        """
        messages.error(request, 'Invalid user role. Please try again.')
        return self._logout_and_render(request)

    def _handle_missing_profile(self, request, profile_type):
        """
        Handles cases where user role exists but profile is missing.
        Logs out user and shows appropriate error message.
        """
        messages.error(request, f'No {profile_type} profile found for this account.')
        return self._logout_and_render(request)

    def _logout_and_render(self, request):
        """
        Utility method to logout user and render homepage.
        Used for error cases that require logout.
        """
        logout(request)
        return render(request, self.TEMPLATE_NAME)

    def _render_home_page(self, request):
        """
        Renders the homepage template for unauthenticated users.
        Includes basic error handling for template rendering.
        """
        try:
            return render(request, self.TEMPLATE_NAME, {})
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return self._logout_and_render(request)
        
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: GetUserProfileView
# Description: Redirects user to role-specific profile page
# Tested On: 
# Status:
# ------------------------------------------------------
class GetUserProfileView(CustomLoginRequiredMixin, View):
    """
    - View for handling user profile redirection based on user role.
    - This view ensures authenticated users are redirected to their appropriate
    profile pages, with proper error handling for invalid roles or exceptions.
    """
    
    # Template and URL constants
    TEMPLATE_NAME = 'home/index.html'
    FREELANCER_PROFILE_URL = 'freelancer:profile'
    CLIENT_PROFILE_URL = 'client:profile'
    HOME_URL = 'home:home'
    
    def get(self, request):
        """
        Handles GET requests for profile redirection:
        - Routes clients to client profile
        - Routes freelancers to freelancer profile
        - Handles invalid roles and exceptions
        """
        try:
            return self._redirect_based_on_role(request)
        except Exception:
            return self._handle_error(request)

    def _redirect_based_on_role(self, request):
        """
        Determines the appropriate redirection based on user role.
        """
        user_role = request.user.role.lower()
        
        role_redirects = {
            'client': self._redirect_to_client_profile,
            'freelancer': self._redirect_to_freelancer_profile,
        }
        
        redirect_handler = role_redirects.get(user_role, self._handle_invalid_role)
        return redirect_handler(request)

    def _redirect_to_client_profile(self, request):
        """Redirects client users to their profile page"""
        return redirect(self.CLIENT_PROFILE_URL)

    def _redirect_to_freelancer_profile(self, request):
        """Redirects freelancer users to their profile page"""
        return redirect(self.FREELANCER_PROFILE_URL)

    def _handle_invalid_role(self, request):
        """
        Handles cases where user has an unrecognized role.
        Logs out user and shows error message.
        """
        messages.error(request, 'Invalid user role. Please try again.')
        return self._logout_and_render(request)

    def _handle_error(self, request):
        """
        Handles unexpected exceptions by redirecting to home
        with an error message.
        """
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect(self.HOME_URL)

    def _logout_and_render(self, request):
        """
        Utility method to logout user and render homepage.
        Used for error cases that require logout.
        """
        logout(request)
        return render(request, self.TEMPLATE_NAME)
   
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: UserSpecificProjectListView
# Description: Redirects client users to their specific project list
# Tested On:
# Status:
# ------------------------------------------------------   
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
        
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: FreelancerListView
# Description: Displays list of freelancers for clients or unauthenticated users
# Tested On:
# Status:
# ------------------------------------------------------    
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
    
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: ProjectListView
# Description: Filters and paginates available projects with advanced options
# Tested On:
# Status:
# ------------------------------------------------------
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
    
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: ProjectDetailView
# Description: Displays individual project detail page with role-based restriction
# Tested On:
# Status:
# ------------------------------------------------------
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

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: handling_404
# Description: Renders custom 404 page template
# Tested On:
# Status:
# ------------------------------------------------------
def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})
