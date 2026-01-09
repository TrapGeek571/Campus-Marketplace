# lostfound/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import LostFoundItem
from .forms import LostFoundItemForm, LostFoundItemSearchForm

def home(request):
    """Home page showing all lost and found items"""
    form = LostFoundItemSearchForm(request.GET or None)
    items = LostFoundItem.objects.all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        
        if search:
            items = items.filter(
                Q(item_name__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        if category:
            items = items.filter(category=category)
        if status:
            items = items.filter(status=status)
    
    # Separate lost and found items
    lost_items = items.filter(status='lost')
    found_items = items.filter(status='found')
    
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
        'form': form,
        'total_items': items.count(),
    }
    return render(request, 'lostfound/home.html', context)

def item_detail(request, pk):
    """View details of a specific item"""
    item = get_object_or_404(LostFoundItem, pk=pk)
    context = {
        'item': item,
    }
    return render(request, 'lostfound/item_detail.html', context)

@login_required
def create_item(request):
    """Create a new lost/found item"""
    if request.method == 'POST':
        form = LostFoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'Your item has been reported successfully!')
            return redirect('lostfound:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LostFoundItemForm()
    
    context = {
        'form': form,
        'title': 'Report Lost/Found Item',
    }
    return render(request, 'lostfound/create_item.html', context)

@login_required
def update_item(request, pk):
    """Update an existing item"""
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Check if user owns the item
    if item.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    if request.method == 'POST':
        form = LostFoundItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('lostfound:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LostFoundItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'title': 'Update Item',
    }
    return render(request, 'lostfound/create_item.html', context)

@login_required
def delete_item(request, pk):
    """Delete an item"""
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Check if user owns the item
    if item.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('lostfound:home')
    
    context = {
        'item': item,
    }
    return render(request, 'lostfound/confirm_delete.html', context)

@login_required
def my_items(request):
    """View user's own lost/found items"""
    items = LostFoundItem.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)
    
    context = {
        'items': items,
        'status_filter': status_filter,
    }
    return render(request, 'lostfound/my_items.html', context)

@login_required
def mark_resolved(request, pk):
    """Mark an item as resolved/returned"""
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    if item.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to update this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    item.is_resolved = True
    item.status = 'returned'
    item.save()
    
    messages.success(request, 'Item marked as resolved!')
    return redirect('lostfound:item_detail', pk=item.pk)