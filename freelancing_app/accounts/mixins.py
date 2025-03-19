from django.contrib.auth.mixins import LoginRequiredMixin

class CustomLoginRequiredMixin(LoginRequiredMixin):
    redirect_field_name = None