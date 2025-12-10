from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from functools import wraps

def login_required_message(view_func):
    """Custom decorator that shows message when login is required."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # For GET requests, show a preview page
            if request.method == 'GET':
                # Check if we want to show a preview
                if request.GET.get('preview'):
                    # Show limited preview
                    return view_func(request, *args, **kwargs)
                else:
                    # Show login prompt
                    messages.warning(request, 'Please login or register to view content.')
                    return redirect(f'{settings.LOGIN_URL}?next={request.path}')
            else:
                # For POST/PUT/DELETE, require login
                messages.warning(request, 'Please login or register to perform this action.')
                return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view