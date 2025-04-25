from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Custom authentication mixin that:
    - Forces login
    - Disables the 'next' parameter
    - Can be extended with additional logic
    """
    login_url = settings.LOGIN_URL  
    redirect_field_name = None     

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
