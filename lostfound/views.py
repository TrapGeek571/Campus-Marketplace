# lostfound/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import LostItem
from .forms import LostItemForm

@login_required
def lost_found_home(request):
    lost_items = LostItem.objects.filter(status='lost').order_by('-created_at')
    found_items = LostItem.objects.filter(status='found').order_by('-created_at')
    
    # Filter by item type
    item_type = request.GET.get('type')
    if item_type:
        lost_items = lost_items.filter(item_type=item_type)
        found_items = found_items.filter(item_type=item_type)
    
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
        'selected_type': item_type,
    }
    return render(request, 'lostfound/home.html', context)

@login_required
def item_detail(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
    # Get similar items (same type)
    similar_items = LostItem.objects.filter(
        item_type=item.item_type,
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
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'Item reported as {item.get_status_display().lower()} successfully!')
            return redirect('lostfound:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LostItemForm()
    
    return render(request, 'lostfound/item_form.html', {
        'form': form,
        'title': 'Report Lost/Found Item',
        'submit_text': 'Report Item',
        'cancel_url': reverse('lostfound:home')
    })

@login_required
def update_item(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
    # Check ownership
    if item.user != request.user:
        messages.error(request, 'You do not have permission to edit this item.')
        return redirect('lostfound:item_detail', pk=item.pk)
    
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('lostfound:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LostItemForm(instance=item)
    
    return render(request, 'lostfound/item_form.html', {
        'form': form,
        'title': 'Update Item',
        'submit_text': 'Update Item',
        'cancel_url': reverse('lostfound:item_detail', pk=item.pk)
    })

@login_required
def delete_item(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
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
    items = LostItem.objects.filter(user=request.user).order_by('-created_at')
    
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
    item = get_object_or_404(LostItem, pk=pk)
    
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