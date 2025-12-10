from django.shortcuts import render
from accounts.decorators import login_required_message

# Create your views here.
@login_required_message
def index(request):
    return render(request, 'housing/index.html', {'title': 'Housing Listings'})