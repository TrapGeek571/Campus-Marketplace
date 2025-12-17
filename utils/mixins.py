from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

class LoginRequiredMixin:
    """Mixin to require login for class-based views"""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
        return super().dispatch(request, *args, **kwargs)