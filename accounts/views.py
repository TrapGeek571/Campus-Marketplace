# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, LoginForm, ProfileUpdateForm
from .models import CustomUser

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
    # Get counts for the profile page
    from marketplace.models import Product
    from lostfound.models import LostItem
    from housing.models import Property
    from food.models import Restaurant
    
    product_count = Product.objects.filter(seller=request.user).count()
    lostitem_count = LostItem.objects.filter(user=request.user).count()
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
        'lostitem_count': lostitem_count,
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
    from lostfound.models import LostItem
    from housing.models import Property
    from food.models import Restaurant
    
    try:
        product_count = Product.objects.filter(seller=user).count()
        lostitem_count = LostItem.objects.filter(user=user).count()
        property_count = Property.objects.filter(owner=user).count()
        restaurant_count = Restaurant.objects.filter(created_by=user).count()
        
        print(f"Counts: products={product_count}, lost={lostitem_count}, properties={property_count}, restaurants={restaurant_count}")
    except Exception as e:
        print(f"Error fetching counts: {e}")
        product_count = 0
        lostitem_count = 0
        property_count = 0
        restaurant_count = 0
    
    context = {
        'user': user,
        'product_count': product_count,
        'lostitem_count': lostitem_count,
        'property_count': property_count,
        'restaurant_count': restaurant_count,
        'title': 'Dashboard'
    }
    
    # Debug: Print context
    print(f"Context being sent: {context}")
    
    return render(request, 'accounts/dashboard.html', context)