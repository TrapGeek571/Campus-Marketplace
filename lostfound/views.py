# lostfound/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import LostFoundItem
from .forms import LostFoundItemForm
import logging

logger = logging.getLogger(__name__)

@login_required
def lost_found_home(request):
    lost_items = LostFoundItem.objects.filter(status='lost').order_by('-created_at')
    found_items = LostFoundItem.objects.filter(status='found').order_by('-created_at')
    
    # Filter by category (CHANGED from item_type to category)
    category = request.GET.get('category')
    if category:
        lost_items = lost_items.filter(category=category)
        found_items = found_items.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        lost_items = lost_items.filter(
            Q(item_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
        found_items = found_items.filter(
            Q(item_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
        'title': 'Lost & Found',
        'search_query': search_query or '',
        'selected_category': category,
    }
    return render(request, 'lostfound/home.html', context)

@login_required
def item_detail(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Get similar items (same category)
    similar_items = LostFoundItem.objects.filter(
        category=item.category,
        status=item.status
    ).exclude(pk=item.pk).order_by('-created_at')[:3]
    
    context = {
        'item': item,
        'similar_items': similar_items,
        'title': f"{item.item_name} - {item.get_status_display()}",
    }
    return render(request, 'lostfound/item_detail.html', context)

@login_required
def report_item(request):
    if request.method == 'POST':
        form = LostFoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'Item reported as {item.get_status_display().lower()} successfully!')
            return redirect('lostfound:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LostFoundItemForm()
    
    return render(request, 'lostfound/item_form.html', {
        'form': form,
        'title': 'Report Lost/Found Item',
        'submit_text': 'Report Item',
        'cancel_url': reverse('lostfound:home')
    })
    
@login_required
def create_item(request):
    if request.method == 'POST':
        # Get form data
        data = request.POST.copy()
        files = request.FILES
        
        # Create item manually to debug
        try:
            item = LostFoundItem(
                user=request.user,
                category=data.get('category'),
                item_name=data.get('item_name'),
                description=data.get('description'),
                location=data.get('location'),
                contact_info=data.get('contact_info'),
                status=data.get('status'),
            )
            
            # Parse date from dd/mm/yyyy to Python date
            date_str = data.get('date_lost', '')
            if date_str:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                item.date_lost = date_obj
            
            # Handle image
            if 'image' in files:
                item.image = files['image']
            
            # Validate and save
            item.full_clean()  # This will validate all fields
            item.save()
            
            messages.success(request, 'Item reported successfully!')
            return redirect('lostfound:home')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            print(f"Error creating item: {e}")
    
    return render(request, 'lostfound/simple_create.html')

@login_required
def update_item(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Check ownership
    if item.user != request.user:
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
    
    return render(request, 'lostfound/item_form.html', {
        'form': form,
        'title': 'Update Item',
        'submit_text': 'Update Item',
        'cancel_url': reverse('lostfound:item_detail', pk=item.pk)
    })

@login_required
def delete_item(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Check ownership
    if item.user != request.user:
        messages.error(request, 'You do not have permission to delete this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('lostfound:home')
    
    return render(request, 'lostfound/item_confirm_delete.html', {
        'item': item,
        'title': 'Delete Item'
    })

@login_required
def my_reports(request):
    items = LostFoundItem.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        items = items.filter(status=status_filter)
    
    context = {
        'items': items,
        'title': 'My Reports',
        'status_filter': status_filter,
    }
    return render(request, 'lostfound/my_reports.html', context)

@login_required
def update_status(request, pk, new_status):
    item = get_object_or_404(LostFoundItem, pk=pk)
    
    # Check ownership
    if item.user != request.user:
        messages.error(request, 'You do not have permission to update this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    valid_statuses = ['lost', 'found', 'returned']
    if new_status in valid_statuses:
        item.status = new_status
        item.save()
        messages.success(request, f'Item status updated to {new_status}!')
    
    return redirect('lostfound:item_detail', pk=item.pk)