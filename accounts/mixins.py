from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

class LoginRequiredMessageMixin(LoginRequiredMixin):
    """Custom mixin that shows a message when login is required."""
    login_url = '/accounts/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login or register to access this page.')
            return redirect(self.login_url + f'?next={request.path}')
        return super().dispatch(request, *args, **kwargs)