from freelancerprofile.models import FreelanceServiceCategory
from projects.models import ProjectCategory, Skill, Project
from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.db.models import Q, Count, Prefetch
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from clientprofile.models import Client
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
import random

# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: HomeView
# Description: Handles routing for authenticated and unauthenticated users
# Tested On: 
# Status:
# Code Refractor Status: In Progress
# ------------------------------------------------------
class HomeView(View):
    """
    - Redirecting authenticated users to appropriate dashboards based on their role
    - Handling cases where user profiles are missing
    - Displaying the homepage for unauthenticated users
    - Managing error cases and logout scenario
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

    def _get_verified_freelancers(self):
        """
        Returns count of verified freelancers with fallback to 0
        """
        try:
            return Freelancer.objects.filter(
                user__is_verified=True
            ).count() or 0
        except Exception:
            return 0

    def _get_completed_projects(self):
        """
        Returns count of completed projects with fallback to 0
        """
        try:
            return Project.objects.filter(
                status=Project.Status.COMPLETED
            ).count() or 0
        except Exception:
            return 0
        
    def _get_client_satisfaction(self):
        """
        Calculates average client satisfaction rating (as percentage)
        Returns float with 1 decimal place, defaulting to 4.3 if no reviews
        """
        try:
            "Code will be added later"
            return 0.0
        except Exception:
            return 0.0
        
    def _get_popular_categories(self):
        """
        Returns top 6 popular categories with freelancer counts and top 4 related skills.
        Freelancer count is based on the number of freelancers who have skills in that category.
        """
        try:
            categories = FreelanceServiceCategory.objects.prefetch_related(
                Prefetch('skills', queryset=Skill.objects.prefetch_related('freelancers'))
            )

            enriched_categories = []

            for category in categories:
                freelancer_ids = Freelancer.objects.filter(
                    skills__in=category.skills.all(),
                    user__is_verified=True
                ).distinct().values_list('id', flat=True)

                category.freelancer_count = len(freelancer_ids)
                skills = list(category.skills.all())
                category.top_skills = random.sample(skills, min(len(skills), 4))
                enriched_categories.append(category)

            return sorted(enriched_categories, key=lambda c: c.freelancer_count, reverse=True)[:6]
        except Exception as e:
            return []
        
    def _get_featured_freelancers(self, limit=6):
        """
        Returns a list of featured freelancers, including badge, skills, and limited details.
        """
        try:
            freelancers = Freelancer.objects.filter(
                is_featured=True,
                user__is_verified=True
            ).select_related('user').prefetch_related('skills')[:limit]

            for freelancer in freelancers:
                all_skills = list(freelancer.skills.all())
                freelancer.display_skills = all_skills[:8]
                freelancer.skills_count = len(all_skills)
            
            return freelancers
        except Exception as e:
            return []

    def _render_home_page(self, request):
        """
        Renders the homepage template for unauthenticated users.
        Includes basic error handling for template rendering.
        """
        try:
            context = {
                'verified_freelancers': self._get_verified_freelancers(),
                'completed_projects': self._get_completed_projects(),
                'client_satisfaction': self._get_client_satisfaction(),
                'popular_categories': self._get_popular_categories(),
                'featured_freelancers': self._get_featured_freelancers(),
            }
            return render(request, self.TEMPLATE_NAME, context)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return self._logout_and_render(request)
        
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: GetUserProfileView
# Description: Redirects user to role-specific profile page
# Tested On: 
# Status:
# Code Refractor Status: In Progress
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
# Code Refractor Status: Not Started
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
# Code Refractor Status: In Progress
# ------------------------------------------------------    
class FreelancerListView(View):
    """
    - Displays list of freelancers for clients or unauthenticated users
    - Implements strict access control (only clients or unauthenticated users)
    - Handles error cases and unauthorized access attempts
    """
    
    # Template and URL constants
    FREELANCER_LIST_TEMPLATE = 'home/freelancerslist.html'
    HOME_URL = 'home:home'
    ITEMS_PER_PAGE = 10
    
    def get(self, request):
        """
        Main entry point for GET requests.
        Verifies access rights before rendering freelancer list.
        """
        try:
            if not self._has_access(request.user):
                return self._handle_unauthorized_access(request)
                
            freelancers = self._get_base_queryset()
            freelancers = self._apply_filters(request, freelancers)
            page_obj = self._paginate_results(request, freelancers)
            
            context = self._build_context(request, page_obj)
            return self._render_freelancer_list(request, context)
        except Exception as e:
            print(e)
            return self._handle_error(request)

    def _has_access(self, user):
        """
        Determines if user has access to view freelancer list.
        Only unauthenticated users or clients are allowed.
        """
        if not user.is_authenticated:
            return True
        return getattr(user, 'role', '').lower() == 'client'
    
    def _get_base_queryset(self):
        """Returns base queryset of active freelancers"""
        return Freelancer.objects.filter(
            user__is_verified=True
        ).select_related('user').prefetch_related('skills').distinct().order_by('-user__date_joined')

    def _apply_filters(self, request, freelancers):
        """Applies all filters from request parameters"""
        freelancers = self._apply_search_filter(request, freelancers)
        freelancers = self._apply_category_filter(request, freelancers)
        freelancers = self._apply_skills_filter(request, freelancers)
        freelancers = self._apply_experience_filter(request, freelancers)
        freelancers = self._apply_availability_filter(request, freelancers)
        freelancers = self._apply_duration_filter(request, freelancers)
        freelancers = self._apply_badge_filter(request, freelancers)
        return freelancers
    
    def _apply_search_filter(self, request, freelancers):
        """Applies keyword search filter"""
        keyword = request.GET.get('search')
        if not keyword:
            return freelancers
            
        return freelancers.filter(
            Q(user__username__icontains=keyword) |
            Q(user__full_name__icontains=keyword) |
            Q(professional_title__icontains=keyword) |
            Q(skills__name__icontains=keyword)
        ).distinct()
        
    def _apply_category_filter(self, request, freelancers):
        """Filters by selected categories"""
        selected_categories = request.GET.getlist('category')
        if not selected_categories or 'all' in selected_categories:
            return freelancers
        return freelancers.filter(
            skills__service_categories__id__in=selected_categories
        ).distinct()
        
    def _apply_experience_filter(self, request, freelancers):
        """Filters by experience level"""
        selected_experience = request.GET.getlist('experience')
        if not selected_experience or 'all' in selected_experience:
            return freelancers
        return freelancers.filter(expertise_level__in=selected_experience)
    
    def _apply_availability_filter(self, request, freelancers):
        """Filters by availability status"""
        selected_availabilities = request.GET.getlist('availability')
        if not selected_availabilities or 'all' in selected_availabilities:
            return freelancers
        return freelancers.filter(availability__in=selected_availabilities)
    
    def _apply_duration_filter(self, request, freelancers):
        """Filters by preferred project duration"""
        selected_durations = request.GET.getlist('duration')
        if not selected_durations or 'all' in selected_durations:
            return freelancers
        return freelancers.filter(preferred_project_duration__in=selected_durations)
    
    def _apply_badge_filter(self, request, freelancers):
        """Filters by badge type"""
        selected_badges = request.GET.getlist('badge')
        if not selected_badges or 'all' in selected_badges:
            return freelancers
        return freelancers.filter(badge__in=selected_badges)
    
    def _apply_skills_filter(self, request, freelancers):
        """Filters by skills"""
        selected_skills = request.GET.getlist('skill')
        if not selected_skills or 'all' in selected_skills:
            return freelancers
        return freelancers.filter(skills__id__in=selected_skills).distinct()
    
    def _paginate_results(self, request, freelancers):
        """Paginates the filtered results"""
        paginator = Paginator(freelancers, self.ITEMS_PER_PAGE)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)
    
    def _build_context(self, request, page_obj):
        """Builds template context with all required data"""
        categories = FreelanceServiceCategory.objects.all()
        skills = Skill.objects.all()
        
        return {
            'freelancers': page_obj,
            'categories': categories,
            'skills': skills,
            'expertise_levels': Freelancer.ExpertiseLevel.choices,
            'availability_options': Freelancer.Availability.choices,
            'duration_options': Freelancer.ProjectDuration.choices,
            'badge_options': Freelancer.BadgeChoices.choices,
            'selected_categories': request.GET.getlist('category'),
            'selected_experience': request.GET.getlist('experience'),
            'selected_availabilities': request.GET.getlist('availability'),
            'selected_durations': request.GET.getlist('duration'),
            'selected_badges': request.GET.getlist('badge'),
            'selected_skills': request.GET.getlist('skill'),
            'search_keyword': request.GET.get('search'),
            'categories_dict': {str(c.id): c for c in categories},
            'skills_dict': {str(s.id): s for s in skills},
        }

    def _render_freelancer_list(self, request, context):
        """Renders the freelancer list template"""
        try:
            return render(request, self.FREELANCER_LIST_TEMPLATE, context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")

    def _handle_unauthorized_access(self, request):
        """
        Handles cases where user doesn't have access rights.
        Redirects to home with appropriate message.
        """
        messages.error(request, 'You do not have permission to view this page.')
        return redirect(self.HOME_URL)

    def _handle_error(self, request):
        """
        Handles unexpected exceptions by redirecting to home
        with an error message.
        """
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect(self.HOME_URL) 
    
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: ProjectListView
# Description: Filters and paginates available projects with advanced options
# Tested On:
# Status:
# Code Refractor Status: In Progress
# ------------------------------------------------------
class ProjectListView(View):
    """
    - Displays filtered and paginated list of published projects
    - Supports advanced filtering by category, skills, budget, duration, etc.
    - Implements strict access control (only freelancers or unauthenticated users)
    - Handles error cases and unauthorized access attempts
    """
    
    # Constants
    PROJECT_LIST_TEMPLATE = 'home/projectlist.html'
    HOME_URL = 'home:home'
    ITEMS_PER_PAGE = 10
    
    def get(self, request):
        """
        Main entry point for GET requests.
        Handles filtering, pagination and template rendering.
        """
        try:
            if not self._has_access(request.user):
                return self._handle_unauthorized_access(request)
                
            projects = self._get_base_queryset()
            projects = self._apply_filters(request, projects)
            page_obj = self._paginate_results(request, projects)
            
            context = self._build_context(request, page_obj)
            return self._render_project_list(request, context)
            
        except Exception as e:
            return self._handle_error(request, str(e))

    def _has_access(self, user):
        """
        Determines if user has access to view project list.
        Only unauthenticated users or freelancers are allowed.
        """
        if not user.is_authenticated:
            return True
        return getattr(user, 'role', '').lower() == 'freelancer'

    def _get_base_queryset(self):
        """Returns base queryset of published projects"""
        return Project.objects.filter(
            status=Project.Status.PUBLISHED
        ).distinct().order_by('-created_at')

    def _apply_filters(self, request, projects):
        """Applies all filters from request parameters"""
        projects = self._apply_search_filter(request, projects)
        projects = self._apply_category_filter(request, projects)
        projects = self._apply_experience_filter(request, projects)
        projects = self._apply_budget_filter(request, projects)
        projects = self._apply_duration_filter(request, projects)
        projects = self._apply_skills_filter(request, projects)
        return projects

    def _apply_search_filter(self, request, projects):
        """Applies keyword search filter"""
        keyword = request.GET.get('search')
        if not keyword:
            return projects
            
        return projects.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(category__name__icontains=keyword) |
            Q(skills_required__name__icontains=keyword)
        ).distinct()

    def _apply_category_filter(self, request, projects):
        """Filters by selected categories"""
        selected_categories = request.GET.getlist('category')
        if not selected_categories or 'all' in selected_categories:
            return projects
        return projects.filter(category_id__in=selected_categories)

    def _apply_experience_filter(self, request, projects):
        """Filters by experience level"""
        selected_experience = request.GET.getlist('experience')
        if not selected_experience or 'all' in selected_experience:
            return projects
        return projects.filter(experience_level__in=selected_experience)

    def _apply_budget_filter(self, request, projects):
        """Filters by budget range"""
        selected_budgets = request.GET.getlist('budget')
        if not selected_budgets or 'all' in selected_budgets:
            return projects
            
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
        return projects.filter(budget_q)

    def _apply_duration_filter(self, request, projects):
        """Filters by project duration"""
        selected_durations = request.GET.getlist('duration')
        if not selected_durations or 'all' in selected_durations:
            return projects
            
        duration_q = Q()
        for d in selected_durations:
            if d == '12+':
                duration_q |= Q(estimated_duration__gte=12)
            else:
                min_d, max_d = map(int, d.split('-'))
                duration_q |= Q(estimated_duration__gte=min_d, estimated_duration__lte=max_d)
        return projects.filter(duration_q)

    def _apply_skills_filter(self, request, projects):
        """Filters by required skills"""
        selected_skills = request.GET.getlist('skill')
        if not selected_skills or 'all' in selected_skills:
            return projects
        return projects.filter(skills_required__id__in=selected_skills).distinct()

    def _paginate_results(self, request, projects):
        """Paginates the filtered results"""
        paginator = Paginator(projects, self.ITEMS_PER_PAGE)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    def _build_context(self, request, page_obj):
        """Builds template context with all required data"""
        categories = ProjectCategory.objects.all()
        skills = Skill.objects.all()
        
        return {
            'projects': page_obj,
            'categories': categories,
            'skills': skills,
            'expertise_levels': Project.ExpertiseLevel.choices,
            'selected_categories': request.GET.getlist('category'),
            'selected_experience': request.GET.getlist('experience'),
            'selected_budgets': request.GET.getlist('budget'),
            'selected_durations': request.GET.getlist('duration'),
            'selected_skills': request.GET.getlist('skill'),
            'search_keyword': request.GET.get('search'),
            'categories_dict': {str(c.id): c for c in categories},
            'skills_dict': {str(s.id): s for s in skills},
        }

    def _render_project_list(self, request, context):
        """Renders the project list template"""
        try:
            return render(request, self.PROJECT_LIST_TEMPLATE, context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")

    def _handle_unauthorized_access(self, request):
        """Handles unauthorized access attempts"""
        messages.error(request, 'You do not have permission to view this page.')
        return redirect(self.HOME_URL)

    def _handle_error(self, request, error_message):
        """Handles unexpected exceptions"""
        messages.error(request, f'Something went wrong. {error_message}')
        return redirect(self.HOME_URL) 
    
# ------------------------------------------------------
# ⏳ [PENDING TEST]
# View Name: ProjectDetailView
# Description: Displays individual project detail page with role-based restriction
# Tested On:
# Status:
# Code Refractor Status: Not Started
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
# Code Refractor Status: Not Started
# ------------------------------------------------------
def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})
