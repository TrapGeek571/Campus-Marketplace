# accounts/views.py
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate, logout , update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from .forms import CustomUserCreationForm, LoginForm, ProfileUpdateForm , DeleteProfilePictureForm
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
import json
from django.db.models import Count
from marketplace.models import Product
from lostfound.models import LostFoundItem
from accounts.models import CustomUser
from datetime import date

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Get statistics
    stats = {
        'total_users': CustomUser.objects.count(),
        'new_users_today': CustomUser.objects.filter(date_joined__date=date.today()).count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'banned_users': CustomUser.objects.filter(is_active=False).count(),
        'total_products': Product.objects.count(),
        'sold_products': Product.objects.filter(is_sold=True).count(),
        'total_lost_items': LostFoundItem.objects.filter(status='lost').count(),
        'total_found_items': LostFoundItem.objects.filter(status='found').count(),
        'total_properties': Property.objects.count(),
        'available_properties': Property.objects.filter(is_available=True).count(),
        'total_restaurants': Restaurant.objects.count(),
        'verified_restaurants': Restaurant.objects.filter(is_verified=True).count(),
    }
    
    # Recent activities
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_products = Product.objects.order_by('-created_at')[:5]
    recent_reports = LostFoundItem.objects.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_products': recent_products,
        'recent_reports': recent_reports,
        'title': 'Admin Dashboard'
    }
    
    return render(request, 'admin/dashboard.html', context)

def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def admin_users_api(request):
    """API endpoint to get all users for admin panel"""
    users = CustomUser.objects.all().values('id', 'username', 'email', 'user_type', 'is_active', 'date_joined')
    users_list = list(users)
    return JsonResponse(users_list, safe=False)

@require_POST
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """API endpoint to ban/unban a user"""
    try:
        target_user = CustomUser.objects.get(id=user_id)
        
        # Prevent admin from banning themselves
        if target_user == request.user:
            return JsonResponse({'success': False, 'message': 'Cannot modify your own status'})
        
        data = json.loads(request.body)
        activate = data.get('activate', False)
        
        target_user.is_active = activate
        target_user.save()
        
        action = "unbanned" if activate else "banned"
        return JsonResponse({
            'success': True, 
            'message': f'User {target_user.username} has been {action}.',
            'is_active': target_user.is_active
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'title': 'Create Account'
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
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
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Login'
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    """View user profile"""
    user = request.user
    context = {
        'user': user,
        'active_tab': 'profile'
    }
    return render(request, 'accounts/profile.html', context)
    # Get counts for the profile page
    from marketplace.models import Product
    from lostfound.models import LostFoundItem
    from housing.models import Property
    from food.models import Restaurant
    
    product_count = Product.objects.filter(seller=request.user).count()
    lostfounditem_count = LostFoundItem.objects.filter(user=request.user).count()
    property_count = Property.objects.filter(owner=request.user).count()
    restaurant_count = Restaurant.objects.filter(created_by=request.user).count()
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'product_count': product_count,
        'lostfounditem_count': lostfounditem_count,
        'property_count': property_count,
        'restaurant_count': restaurant_count,
        'title': 'My Profile'
    })

@login_required
def dashboard_view(request):
    user = request.user
    
    # Debug: Print to console
    print(f"Dashboard accessed by: {user.username}")
    
    # Get counts for dashboard
    from marketplace.models import Product
    from lostfound.models import LostFoundItem
    from housing.models import Property
    from food.models import Restaurant
    
    try:
        product_count = Product.objects.filter(seller=user).count()
        lostfounditem_count = LostFoundItem.objects.filter(user=user).count()
        property_count = Property.objects.filter(owner=user).count()
        restaurant_count = Restaurant.objects.filter(created_by=user).count()
        
        print(f"Counts: products={product_count}, lost={lostfounditem_count}, properties={property_count}, restaurants={restaurant_count}")
    except Exception as e:
        print(f"Error fetching counts: {e}")
        product_count = 0
        lostfounditem_count = 0
        property_count = 0
        restaurant_count = 0
    
    context = {
        'user': user,
        'product_count': product_count,
        'lostfounditem_count': lostfounditem_count,
        'property_count': property_count,
        'restaurant_count': restaurant_count,
        'title': 'Dashboard'
    }
    
    # Debug: Print context
    print(f"Context being sent: {context}")
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'active_tab': 'edit_profile'
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def delete_profile_picture(request):
    """Delete user's profile picture"""
    user = request.user
    
    if request.method == 'POST':
        form = DeleteProfilePictureForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            # Delete the profile picture from Cloudinary
            if user.profile_picture:
                user.profile_picture.delete()
                user.profile_picture = None
                user.save()
                messages.success(request, 'Profile picture deleted successfully!')
            else:
                messages.info(request, 'You don\'t have a profile picture to delete.')
            return redirect('accounts:profile_edit')
    else:
        form = DeleteProfilePictureForm()
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'accounts/delete_profile_picture.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'active_tab': 'change_password'
    }
    return render(request, 'accounts/change_password.html', context)