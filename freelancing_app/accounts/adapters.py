from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        # Store current date in session
        request.session['oauth_timestamp'] = timezone.now().isoformat()
        
        # Get email from the social account data
        email = sociallogin.account.extra_data.get('email')
        
        # Check if user with this email already exists
        if sociallogin.is_existing:
            # User already exists - continue with normal login flow
            return
        else:
            # New user - store data in session and redirect to role selection
            request.session['sociallogin_provider'] = sociallogin.account.provider
            request.session['sociallogin_email'] = email
            request.session['sociallogin'] = sociallogin.serialize()
            
            # Force immediate redirect to role selection page
            raise ImmediateHttpResponse(redirect(reverse('account:oauth_role_selection')))

# Add a custom account adapter to handle the connect form
class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Always allow signup
        return True
        
    def is_auto_signup_allowed(self, request):
        """
        Prevent auto signup for social accounts
        """
        return False 