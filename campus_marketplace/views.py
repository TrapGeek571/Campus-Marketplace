from django.http import HttpResponseForbidden
from marketplace.models import Product
from lostfound.models import LostItem
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item
from .forms import ItemForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Campus Marketplace.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'marketplace/register.html', {'form': form})



# Update your existing views to require login
@login_required
def product_list(request, category=None):
    if category:
        items = Item.objects.filter(category=category)
    else:
        items = Item.objects.all()
    
    categories = dict(Item.CATEGORY_CHOICES)
    context = {
        'items': items,
        'category': category,
        'category_display': categories.get(category, 'All Items'),
    }
    return render(request, 'marketplace/product_list.html', context)

@login_required
def marketplace_items(request):
    return product_list(request, category='marketplace')

@login_required
def lost_found_items(request):
    return product_list(request, category='lost_found')

@login_required
def housing_items(request):
    return product_list(request, category='housing')

@login_required
def food_items(request):
    return product_list(request, category='food')

@login_required
def add_item(request, category='marketplace'):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.category = category
            item.save()
            return redirect('product_list', category=category)
    else:
        form = ItemForm()
    
    categories = dict(Item.CATEGORY_CHOICES)
    context = {
        'form': form,
        'category': category,
        'category_display': categories.get(category, 'Marketplace'),
    }
    return render(request, 'marketplace/add_item.html', context)