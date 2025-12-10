from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm
from lostfound.models import LostItem
from .models import Profile

# ========== HELPER FUNCTIONS ==========
def get_or_create_profile(user):
    """Get user profile or create if doesn't exist."""
    try:
        return user.profile
    except Profile.DoesNotExist:
        return Profile.objects.create(user=user)

# ========== AUTHENTICATION VIEWS ==========
def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure profile is created
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Account created for {user.username}! Welcome to Campus Marketplace!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

# ========== PROFILE VIEWS ==========
@login_required
def profile(request):
    """Display user profile with stats."""
    user = request.user
    profile_obj = get_or_create_profile(user)
    
    # Get user's stats
    lost_items_count = LostItem.objects.filter(user=user).count()
    lost_items = LostItem.objects.filter(user=user, item_type='lost').count()
    found_items = LostItem.objects.filter(user=user, item_type='found').count()
    returned_items = LostItem.objects.filter(user=user, status='returned').count()
    
    context = {
        'user': user,
        'profile': profile_obj,
        'lost_items_count': lost_items_count,
        'lost_items': lost_items,
        'found_items': found_items,
        'returned_items': returned_items,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Handle profile editing."""
    user = request.user
    profile_obj = get_or_create_profile(user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_obj)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def user_profile(request, username):
    """View other users' public profiles."""
    user = get_object_or_404(User, username=username)
    profile_obj = get_or_create_profile(user)
    
    # Only show active lost/found items (not returned)
    user_items = LostItem.objects.filter(user=user).exclude(status='returned')[:5]
    total_items = LostItem.objects.filter(user=user).count()
    
    context = {
        'viewed_user': user,
        'user_profile': profile_obj,
        'user_items': user_items,
        'total_items': total_items,
    }
    return render(request, 'accounts/user_profile.html', context)