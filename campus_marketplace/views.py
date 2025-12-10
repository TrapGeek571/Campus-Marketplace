from django.shortcuts import render
from django.http import HttpResponseForbidden

def home(request):
    return render(request, 'home.html')

def test_view(request):
    return HttpResponseForbidden("You do not have permission to access this resource.")

def handler403(request, exception=None):
    """Custom 403 handler."""
    return render(request, '403.html', status=403)