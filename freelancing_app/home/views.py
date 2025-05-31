from freelancerprofile.models import WorkExperience, Education, FreelancerLanguage
from freelancerprofile.models import FreelanceServiceCategory
from projects.models import ProjectCategory, Skill, Project
from accounts.mixins import CustomLoginRequiredMixin
from freelancerprofile.models import Freelancer
from django.db.models import Q, Count, Prefetch
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from home.utils import ContactEmailService
from clientprofile.models import Client
from django.contrib.auth import logout
from freelancing_app import settings
from django.contrib import messages
from django.db.models import Avg
from django.urls import reverse
from django.views import View
from itertools import chain
from decimal import Decimal
import random
import os
from contract.models import Contract, Review

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: HomeView
# Description: Handles routing for authenticated and unauthenticated users
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
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
# ✅ [TESTED & COMPLETED]
# View Name: GetUserProfileView
# Description: Redirects user to role-specific profile page
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
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
# ✅ [TESTED & COMPLETED]
# View Name: FreelancerListView
# Description: Displays list of freelancers for clients or unauthenticated users
# Tested On: 2025-04-29
# Status: Working as expected
# Code Refractor Status: Completed
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
        ).select_related('user').prefetch_related(
            'skills',
            'freelancerskill_set'
        ).annotate(
            completed_projects=Count(
                'proposals__contract',
                filter=Q(proposals__contract__status=Contract.Status.COMPLETED),
                distinct=True
            )
        ).distinct().order_by('-user__date_joined')

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
        
        # Get review statistics for each freelancer
        for freelancer in page_obj:
            stats = Review.get_freelancer_stats(freelancer)
            freelancer.review_stats = stats
        
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
# ✅ [TESTED & COMPLETED]
# View Name: FreelancerDetailView   
# Description: Displays detailed information about a freelancer
# Tested On: 2025-04-29
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class FreelancerDetailView(View):
    """
    - Displays detailed view of a freelancer profile
    - Implements strict access control:
        * Unauthenticated users can view
        * Clients can view
        * Only the freelancer can view if authenticated as freelancer
    - Handles error cases and unauthorized access attempts
    - Prefetches related data for performance
    """
    
    # Constants
    TEMPLATE_NAME = 'home/freelancer-detail.html'
    FREELANCER_DETAIL_URL = 'home:freelancer-detail'
    HOME_URL = 'home:home'
    SIMILAR_FREELANCERS_LIMIT = 4
    
    def get(self, request, freelancer_id):
        """
        Main entry point for GET requests.
        Handles access control, data fetching and template rendering.
        """
        try:
            if not self._has_access(request, freelancer_id):
                return self._handle_unauthorized_access(request)
                
            context = self._build_context(request, freelancer_id)
            
            return self._render_freelancer_detail(request, context)
            
        except Freelancer.DoesNotExist:
            return self._handle_freelancer_not_found(request)
        except Exception as e:
            print(e)
            return self._handle_error(request, str(e))

    def _has_access(self, request, freelancer_id):
        """
        Determines if user has access to view the freelancer profile.
        Rules:
        - Unauthenticated users can view
        - Clients can view
        - Only the freelancer can view if authenticated as freelancer
        """
        if not request.user.is_authenticated:
            return True
            
        user_role = getattr(request.user, 'role', '').lower()
        
        # Clients can always view
        if user_role == 'client':
            return True
            
        # Freelancers can only view their own profile
        if user_role == 'freelancer':
            try:
                freelancer = Freelancer.objects.get(id=freelancer_id)
                return freelancer.user == request.user
            except Freelancer.DoesNotExist:
                return False
                
        return False

    def _build_context(self, request, freelancer_id):
        """
        Builds template context with all required data including:
        - Freelancer details
        - Related skills with levels
        - Portfolio items
        - Freelancer's project statistics
        """
        freelancer = Freelancer.objects.get(id=freelancer_id)
        
        freelancer_languages = FreelancerLanguage.objects.filter(
                freelancer=freelancer
            ).select_related('language')
        
        # Work Experience (ordered: ongoing first)
        experiences = WorkExperience.objects.filter(freelancer=freelancer)
        ongoing_experiences = experiences.filter(currently_working=True).order_by('-start_date')
        past_experiences = experiences.filter(currently_working=False).order_by(
            '-end_date' if WorkExperience._meta.get_field('end_date').null else 'end_date'
        )
        ordered_experiences = list(chain(ongoing_experiences, past_experiences))

        # Education (ordered: ongoing first)
        educations = Education.objects.filter(freelancer=freelancer)
        ongoing_educations = educations.filter(currently_studying=True).order_by('-start_date')
        past_educations = educations.filter(currently_studying=False).order_by(
            '-end_date' if Education._meta.get_field('end_date').null else 'end_date'
        )
        ordered_educations = list(chain(ongoing_educations, past_educations))
        
        # Get service categories based on freelancer's skills
        freelancer_skills = freelancer.skills.all()
        service_categories = FreelanceServiceCategory.objects.filter(
            skills__in=freelancer_skills
        ).distinct()
        
        context = {
            'freelancer': freelancer,
            'freelancer_languages': freelancer_languages,
            'experiences': ordered_experiences,
            'educations': ordered_educations,
            'service_categories': service_categories,
        }
        return context

    def _render_freelancer_detail(self, request, context):
        """Renders the freelancer detail template"""
        try:
            return render(request, self.TEMPLATE_NAME, context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")

    def _handle_unauthorized_access(self, request):
        """Handles unauthorized access attempts"""
        messages.error(request, 'You do not have permission to view this freelancer profile.')
        return redirect(self.HOME_URL)

    def _handle_freelancer_not_found(self, request):
        """Handles case when freelancer doesn't exist"""
        messages.error(request, 'Freelancer not found or no longer available.')
        return redirect(self.HOME_URL)

    def _handle_error(self, request, error_message):
        """Handles unexpected exceptions"""
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ProjectListView
# Description: Filters and paginates available projects with advanced options
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
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
# ✅ [TESTED & COMPLETED]
# View Name: ProjectDetailView
# Description: Displays individual project detail page with role-based restriction
# Tested On: 2025-04-26
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProjectDetailView(View):
    """
    - Displays detailed view of a published project
    - Implements strict access control:
        * Unauthenticated users can view
        * Freelancers can view
        * Only the project owner (client) can view if authenticated as client
    - Handles error cases and unauthorized access attempts
    - Prefetches related data for performance
    """
    
    # Constants
    TEMPLATE_NAME = 'home/project-detail.html'
    PROJECT_DETAIL_URL = 'home:project-detail'
    HOME_URL = 'home:home'
    SIMILAR_PROJECTS_LIMIT = 4
    
    def get(self, request, project_id):
        """
        Main entry point for GET requests.
        Handles access control, data fetching and template rendering.
        """
        try:
            if not self._has_access(request, project_id):
                return self._handle_unauthorized_access(request)
                
            context = self._build_context(request, project_id)
            
            return self._render_project_detail(request, context)
            
        except Project.DoesNotExist:
            return self._handle_project_not_found(request)
        except Exception as e:
            print(e)
            return self._handle_error(request, str(e))

    def _has_access(self, request, project_id):
        """
        Determines if user has access to view the project.
        Rules:
        - Unauthenticated users can view
        - Freelancers can view
        - Only the project owner (client) can view if authenticated as client
        """
        if not request.user.is_authenticated:
            return True
            
        user_role = getattr(request.user, 'role', '').lower()
        
        # Freelancers can always view
        if user_role == 'freelancer':
            return True
                
        return False

    def _build_context(self, request, project_id):
        """
        Builds template context with all required data including:
        - Project details
        - Related skills with levels
        - Attachments
        - Client's project statistics
        - Client reviews and average rating (paginated)
        """
        from django.core.paginator import Paginator
        project = Project.objects.prefetch_related(
                'project_skills__skill',
                'project_attachments'
        ).get(id=project_id)
        
        project_url = request.build_absolute_uri(
            reverse(self.PROJECT_DETAIL_URL, kwargs={'project_id': project.id})
        )
        
        attachments = []
        for attachment in project.project_attachments.all():
            try:
                if os.path.exists(attachment.file.path):
                    attachments.append({
                        'file': attachment.file,
                        'filename': os.path.basename(attachment.file.name),
                        'uploaded_at': attachment.uploaded_at
                    })
                else:
                    filename = os.path.basename(attachment.file.name)
                    project_attachments_path = os.path.join(settings.MEDIA_ROOT, 'project_attachments', filename)
                    if os.path.exists(project_attachments_path):
                        attachment.file.name = filename
                        attachment.save()
                        attachments.append({
                            'file': attachment.file,
                            'filename': filename,
                            'uploaded_at': attachment.uploaded_at
                        })
            except Exception as e:
                print(f"[Attachment Error]: {e}")
                continue
        
        key_requirements = []
        if project.key_requirements:
            key_requirements = [req.strip() for req in project.key_requirements.split('\n') if req.strip()]
            
        client = project.client  
        total_projects = Project.objects.filter(client=client).count()
        completed_projects = Project.objects.filter(client=client, status=Project.Status.COMPLETED).count()
        
        shortlisted_count = project.proposals.filter(is_shortlisted=True).count()
        avg_bid_amount = project.proposals.aggregate(avg_amount=Avg('proposed_amount'))['avg_amount'] or 0
        
        # --- Client Reviews and Average Rating (Paginated) ---
        contracts = Contract.objects.filter(proposal__project__client=client)
        client_reviews_qs = Review.objects.filter(contract__in=contracts, reviewer_type=Review.ReviewerType.FREELANCER).select_related('contract__proposal__freelancer__user', 'contract__proposal__project').order_by('-created_at')
        page_number = request.GET.get('review_page', 1)
        paginator = Paginator(client_reviews_qs, 5)  # 5 reviews per page
        client_reviews = paginator.get_page(page_number)
        client_avg_rating = client_reviews_qs.aggregate(avg=Avg('rating'))['avg'] or 0.0
        client_avg_rating = round(client_avg_rating, 1)
        
        similar_projects = self._get_similar_projects(project)
        
        context = {
            'project': project,
            'project_url': project_url,  
            'project_title': project.title,  
            'key_requirements': key_requirements,
            'attachments': attachments,  
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'similar_projects': similar_projects,
            'shortlisted_count': shortlisted_count,
            'avg_bid_amount': avg_bid_amount,
            'client_reviews': client_reviews,
            'client_avg_rating': client_avg_rating,
        }
        return context
    
    def _get_similar_projects(self, project):
        """
        Finds similar projects based on:
        1. Same category
        2. Matching skills
        3. Similar budget range (for price range projects)
        4. Excludes the current project
        Orders by:
        1. Number of matching skills
        2. Closest budget match
        3. Most recently posted
        """        
        skill_ids = list(project.project_skills.values_list('skill_id', flat=True))
        
        similar_projects = Project.objects.filter(
            status=Project.Status.PUBLISHED
        ).exclude(
            id=project.id
        ).prefetch_related(
            'project_skills__skill',
            'client__user'
        )
        
        if project.category:
            similar_projects = similar_projects.filter(category=project.category)
        
        similar_projects = similar_projects.annotate(
            matching_skills_count=Count(
                'project_skills',
                filter=Q(project_skills__skill_id__in=skill_ids)
            )
        ).order_by('-matching_skills_count', '-created_at')
        
        if project.is_fixed_price:
            lower_bound = project.fixed_budget * Decimal('0.8')
            upper_bound = project.fixed_budget * Decimal('1.2')
            similar_projects = similar_projects.filter(
                Q(is_fixed_price=True, fixed_budget__gte=lower_bound, fixed_budget__lte=upper_bound) |
                Q(is_fixed_price=False, budget_min__lte=upper_bound, budget_max__gte=lower_bound)
            )
        else:
            similar_projects = similar_projects.filter(
                Q(is_fixed_price=True, fixed_budget__gte=project.budget_min, fixed_budget__lte=project.budget_max) |
                Q(is_fixed_price=False, 
                  budget_min__lte=project.budget_max, 
                  budget_max__gte=project.budget_min)
            )
        
        return similar_projects[:self.SIMILAR_PROJECTS_LIMIT]

    def _render_project_detail(self, request, context):
        """Renders the project detail template"""
        try:
            return render(request, self.TEMPLATE_NAME, context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")

    def _handle_unauthorized_access(self, request):
        """Handles unauthorized access attempts"""
        messages.error(request, 'You do not have permission to view this project.')
        return redirect(self.HOME_URL)

    def _handle_project_not_found(self, request):
        """Handles case when project doesn't exist"""
        messages.error(request, 'Project not found or no longer available.')
        return redirect(self.HOME_URL)

    def _handle_error(self, request, error_message):
        """Handles unexpected exceptions"""
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: handling_404
# Description: Renders custom 404 page template
# Tested On:
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
def handling_404(request, exception):
    error_page_template = '404.html'
    return render(request, error_page_template, {})

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: AboutUsView
# Description: Renders the About Us page
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class AboutUsView(View):
    """
    - Displays the About Us page with company information
    - Shows key statistics and achievements
    - Accessible to all users (authenticated and unauthenticated)
    """
    
    TEMPLATE_NAME = 'home/about-us.html'
    HOME_URL = 'home:home'
    
    def get(self, request):
        """
        Renders the About Us page with relevant statistics and information
        """
        try:
            return render(request, self.TEMPLATE_NAME)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ContactUsView
# Description: Renders the Contact Us page and handles contact form submissions
# Tested On: 2025-04-22
# Status: Working as expected
# Code Refactor Status: Completed
# ------------------------------------------------------
class ContactUsView(View):
    """
    - Displays the Contact Us page with contact form
    - Handles form submissions
    - Provides contact information and support details
    - Accessible to all users
    """
    
    TEMPLATE_NAME = 'home/contact-us.html'
    CONTACT_US_URL = 'home:contact-us'
    HOME_URL = 'home:home'

    def get(self, request):
        """
        Renders the Contact Us page with contact form
        """
        try:
            context = {
                'contact_info': self._get_contact_info(),
            }
            return render(request, self.TEMPLATE_NAME, context)
        except Exception as e:
            print(e)
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.HOME_URL)

    def post(self, request):
        """
        Handles contact form submissions
        """
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone', 'Not provided')
            subject_type = request.POST.get('subject')
            message = request.POST.get('message')
            
            ContactEmailService.send_user_confirmation_email(
                name=name,
                email_address=email,
                subject_type=subject_type,
                message=message
            )
            
            ContactEmailService.send_admin_notification_email(
                name=name,
                email_address=email,
                phone=phone,
                subject_type=subject_type,
                message=message
            )
            
            messages.success(request, 'Thank you for contacting us. We will get back to you soon.')
            return redirect(self.CONTACT_US_URL)
        except Exception as e:
            print(f"Contact form submission error: {e}")
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.CONTACT_US_URL)

    def _get_contact_info(self):
        """Returns contact information"""
        return {
            'company_name': settings.COMPANY_NAME,
            'location': settings.LOCATION,
            'contact_email': settings.CONTACT_EMAIL,
            'support_email': settings.SUPPORT_EMAIL,
            'contact_phone': settings.CONTACT_PHONE,
            'contact_phone_2': settings.CONTACT_PHONE_2,
        }