from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account authentication that:
    - Handles existing user conflicts
    - Manages OAuth flow with role selection
    - Tracks OAuth timestamps
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Intercept social login process to:
        1. Track OAuth timestamp
        2. Handle existing user conflicts
        3. Redirect new users to role selection
        
        Args:
            request: HttpRequest object
            sociallogin: SocialLogin instance
            
        Raises:
            ImmediateHttpResponse when redirecting
        """
        self._store_oauth_timestamp(request)
        email = self._extract_email(sociallogin)
        
        try:
            user = User.objects.get(email=email)
            self._handle_existing_user(request, user)
        except ObjectDoesNotExist:
            self._prepare_new_user_flow(request, sociallogin, email)

    def _store_oauth_timestamp(self, request):
        """Store OAuth timestamp in session for tracking"""
        request.session['oauth_timestamp'] = timezone.now().isoformat()

    def _extract_email(self, sociallogin):
        """Extract email from social account data"""
        return sociallogin.account.extra_data.get('email')

    def _handle_existing_user(self, request, user):
        """
        Handle cases where user already exists in system
        
        Args:
            request: HttpRequest object
            user: Existing User instance
            
        Raises:
            ImmediateHttpResponse when redirecting
        """
        if user.auth_method == 'traditional':
            messages.error(
                request,
                'This email is already registered with password. '
                'Please login using your password.'
            )
            raise ImmediateHttpResponse(redirect(reverse('account:login')))
        # For existing OAuth users, let normal flow continue

    def _prepare_new_user_flow(self, request, sociallogin, email):
        """
        Prepare session for new user registration flow
        
        Args:
            request: HttpRequest object
            sociallogin: SocialLogin instance
            email: Extracted email address
            
        Raises:
            ImmediateHttpResponse to redirect to role selection
        """
        request.session.update({
            'sociallogin_provider': sociallogin.account.provider,
            'sociallogin_email': email,
            'sociallogin': sociallogin.serialize()
        })
        raise ImmediateHttpResponse(
            redirect(reverse('account:oauth_role_selection'))
        )

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter that modifies default allauth behavior:
    - Always allows signups
    - Disables auto signup for social accounts
    """
    
    def is_open_for_signup(self, request):
        """
        Determine if new signups are allowed
        
        Args:
            request: HttpRequest object
            
        Returns:
            bool: Always True to allow signups
        """
        return True
        
    def is_auto_signup_allowed(self, request):
        """
        Determine if auto signup is allowed for social accounts
        
        Args:
            request: HttpRequest object
            
        Returns:
            bool: Always False to require role selection
        """
        return False