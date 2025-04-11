from django.contrib.auth.mixins import LoginRequiredMixin

class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Custom authentication mixin that extends Django's LoginRequiredMixin.
    
    This mixin:
    - Requires users to be authenticated to access the view
    - Removes the 'next' parameter from redirect URLs by setting redirect_field_name to None
    - Can be easily extended with additional custom authentication logic
    
    Usage:
        class MyView(CustomLoginRequiredMixin, View):
            # Your view implementation
    """
    
    redirect_field_name = None  # Disables the 'next' parameter in redirect URLs
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add custom pre-authentication logic if needed
        """
        # Add any custom pre-authentication logic here if required
        return super().dispatch(request, *args, **kwargs)