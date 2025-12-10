from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required , user_passes_test
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from .models import LostItem
from .forms import LostItemForm
from accounts.decorators import login_required_message

@login_required_message
def index(request):
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    item_type = request.GET.get('type', '')
    
    items = LostItem.objects.all()
    
    if search_query:
        items = items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_lost__icontains=search_query) |
            Q(location_found__icontains=search_query)
        )
    
    if category:
        items = items.filter(category=category)
    
    if item_type:
        items = items.filter(item_type=item_type)
    
    # Separate lost and found items
    lost_items = items.filter(item_type='lost', status='lost')
    found_items = items.filter(item_type='found', status='found')
    
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
        'search_query': search_query,
        'category': category,
        'item_type': item_type,
        'categories': LostItem.CATEGORY_CHOICES,
    }
    return render(request, 'lostfound/index.html', context)

@login_required_message
def create(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.status = item.item_type  # Set status based on item_type
            item.save()
            messages.success(request, f'Your {item.item_type} item has been posted!')
            return redirect('lostfound:index')
    else:
        form = LostItemForm()
    
    return render(request, 'lostfound/create.html', {'form': form})

@login_required_message
def detail(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    return render(request, 'lostfound/detail.html', {'item': item})

@login_required_message
def mark_returned(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
    # Only allow if user owns the item or is marking their found item as returned
    if request.user == item.user:
        item.status = 'returned'
        item.save()
        messages.success(request, f'Item marked as returned!')
    
    return redirect('lostfound:detail', pk=pk)

@login_required_message
def edit(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
    # Check permissions
    if not item.can_edit(request.user):
        raise PermissionDenied("You don't have permission to edit this item.")
    
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            # Don't change user when editing
            form.save()
            messages.success(request, f'Item has been updated successfully!')
            return redirect('lostfound:detail', pk=item.pk)
    else:
        form = LostItemForm(instance=item)
    
    return render(request, 'lostfound/edit.html', {'form': form, 'item': item})

@login_required_message
def delete(request, pk):
    item = get_object_or_404(LostItem, pk=pk)
    
    # Check permissions
    if not item.can_delete(request.user):
        raise PermissionDenied("You don't have permission to delete this item.")
    
    if request.method == 'POST':
        # Double-check confirmation
        confirm_text = request.POST.get('confirm_text', '').upper()
        if confirm_text != 'DELETE':
            messages.error(request, 'Please type "DELETE" to confirm deletion.')
            return render(request, 'lostfound/delete.html', {'item': item})
        
        item_title = item.title
        item.delete()
        messages.success(request, f'Item "{item_title}" has been deleted successfully!')
        return redirect('lostfound:index')
    
    return render(request, 'lostfound/delete.html', {'item': item})

# Add admin-only view for managing all items
@login_required_message
@user_passes_test(lambda u: u.is_superuser)
def admin_manage(request):
    """Admin view to see and manage all items."""
    items = LostItem.objects.all().order_by('-created_at')
    users = User.objects.all()
    
    # Calculate counts
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    
    context = {
        'items': items,
        'total_count': items.count(),
        'lost_count': items.filter(item_type='lost').count(),
        'found_count': items.filter(item_type='found').count(),
        'returned_count': items.filter(status='returned').count(),
        'today_count': items.filter(created_at__date=today).count(),
        'week_count': items.filter(created_at__gte=week_ago).count(),
        'user_count': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'top_users': User.objects.annotate(
            item_count=Count('lostitem')
        ).order_by('-item_count')[:5],
    }
    return render(request, 'lostfound/admin_manage.html', context)