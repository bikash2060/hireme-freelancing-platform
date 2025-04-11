from django.utils import timezone
from django.contrib.auth import get_user_model

class UserActivityMiddleware:
    """
    Middleware to track user activity by updating last_activity timestamp.
    
    Features:
    - Updates last_activity field for authenticated users on each request
    - Efficiently updates only the last_activity field
    - Handles potential database errors gracefully
    - Lightweight with minimal performance impact
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.User = get_user_model()

    def __call__(self, request):
        """
        Process the request and update user activity if authenticated.
        """
        self._update_user_activity(request)
        return self.get_response(request)

    def _update_user_activity(self, request):
        """
        Internal method to update the user's last activity timestamp.
        """
        try:
            if request.user.is_authenticated:
                # Use update() for better performance and to avoid race conditions
                self.User.objects.filter(pk=request.user.pk).update(
                    last_activity=timezone.now()
                )
        except Exception as e:
            # Log the error in production (consider using logging module)
            pass  # Silently fail to not interrupt the request flow