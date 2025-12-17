# food/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import Restaurant, MenuItem
from .forms import RestaurantForm, MenuItemForm

@login_required
def food_home(request):
    restaurants = Restaurant.objects.filter(is_verified=True).order_by('-created_at')
    
    # Filter by cuisine
    cuisine = request.GET.get('cuisine')
    if cuisine:
        restaurants = restaurants.filter(cuisine=cuisine)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        restaurants = restaurants.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Filter by verified status (admin only)
    if request.user.is_staff:
        show_all = request.GET.get('show_all')
        if show_all == 'true':
            restaurants = Restaurant.objects.all().order_by('-created_at')
    
    context = {
        'restaurants': restaurants,
        'title': 'Food & Restaurants',
        'search_query': search_query or '',
        'selected_cuisine': cuisine,
    }
    return render(request, 'food/home.html', context)

@login_required
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.filter(is_available=True)
    
    # Get similar restaurants (same cuisine)
    similar_restaurants = Restaurant.objects.filter(
        cuisine=restaurant.cuisine,
        is_verified=True
    ).exclude(pk=restaurant.pk).order_by('-created_at')[:3]
    
    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'similar_restaurants': similar_restaurants,
        'title': restaurant.name,
    }
    return render(request, 'food/restaurant_detail.html', context)

@login_required
def create_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.created_by = request.user
            
            # Auto-verify if user is staff
            if request.user.is_staff:
                restaurant.is_verified = True
            
            restaurant.save()
            messages.success(request, 'Restaurant submitted successfully! It will be visible after verification.')
            return redirect('food:restaurant_detail', pk=restaurant.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RestaurantForm()
    
    return render(request, 'food/restaurant_form.html', {
        'form': form,
        'title': 'Add Restaurant',
        'submit_text': 'Submit Restaurant',
        'cancel_url': reverse('food:home')
    })

@login_required
def update_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    
    # Check ownership or staff status
    if restaurant.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this restaurant.')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully!')
            return redirect('food:restaurant_detail', pk=restaurant.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RestaurantForm(instance=restaurant)
    
    return render(request, 'food/restaurant_form.html', {
        'form': form,
        'title': 'Edit Restaurant',
        'submit_text': 'Update Restaurant',
        'cancel_url': reverse('food:restaurant_detail', pk=restaurant.pk)
    })

@login_required
def delete_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    
    # Check ownership or staff status
    if restaurant.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this restaurant.')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully!')
        return redirect('food:home')
    
    return render(request, 'food/restaurant_confirm_delete.html', {
        'restaurant': restaurant,
        'title': 'Delete Restaurant'
    })

@login_required
def my_restaurants(request):
    restaurants = Restaurant.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'restaurants': restaurants,
        'title': 'My Restaurants',
    }
    return render(request, 'food/my_restaurants.html', context)

@login_required
def create_menu_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    
    # Check ownership
    if restaurant.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to add menu items.')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('food:restaurant_detail', pk=restaurant.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MenuItemForm()
    
    return render(request, 'food/menu_item_form.html', {
        'form': form,
        'title': 'Add Menu Item',
        'restaurant': restaurant,
        'submit_text': 'Add Menu Item',
        'cancel_url': reverse('food:restaurant_detail', pk=restaurant.pk)
    })

@login_required
def update_menu_item(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)
    restaurant = menu_item.restaurant
    
    # Check ownership
    if restaurant.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this menu item.')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('food:restaurant_detail', pk=restaurant.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MenuItemForm(instance=menu_item)
    
    return render(request, 'food/menu_item_form.html', {
        'form': form,
        'title': 'Edit Menu Item',
        'restaurant': restaurant,
        'menu_item': menu_item,
        'submit_text': 'Update Menu Item',
        'cancel_url': reverse('food:restaurant_detail', pk=restaurant.pk)
    })

@login_required
def delete_menu_item(request, pk):
    menu_item = get_object_or_404(MenuItem, pk=pk)
    restaurant = menu_item.restaurant
    
    # Check ownership
    if restaurant.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this menu item.')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('food:restaurant_detail', pk=restaurant.pk)
    
    return render(request, 'food/menu_item_confirm_delete.html', {
        'menu_item': menu_item,
        'restaurant': restaurant,
        'title': 'Delete Menu Item'
    })

# Admin-only views
@login_required
def verify_restaurant(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to verify restaurants.')
        return redirect('food:restaurant_detail', pk=pk)
    
    restaurant = get_object_or_404(Restaurant, pk=pk)
    restaurant.is_verified = True
    restaurant.save()
    messages.success(request, f'{restaurant.name} has been verified!')
    return redirect('food:restaurant_detail', pk=restaurant.pk)