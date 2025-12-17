# housing/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import Property
from .forms import PropertyForm

@login_required
def housing_home(request):
    properties = Property.objects.filter(is_available=True).order_by('-created_at')
    
    # Filter by property type
    property_type = request.GET.get('type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Price range filter
    min_rent = request.GET.get('min_rent')
    max_rent = request.GET.get('max_rent')
    if min_rent:
        properties = properties.filter(rent__gte=min_rent)
    if max_rent:
        properties = properties.filter(rent__lte=max_rent)
    
    # Bedrooms filter
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        properties = properties.filter(bedrooms=bedrooms)
    
    # Furnished filter
    furnished = request.GET.get('furnished')
    if furnished == 'yes':
        properties = properties.filter(is_furnished=True)
    elif furnished == 'no':
        properties = properties.filter(is_furnished=False)
    
    context = {
        'properties': properties,
        'title': 'Housing',
        'search_query': search_query or '',
        'selected_type': property_type,
    }
    return render(request, 'housing/home.html', context)

@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    # Get similar properties (same type, excluding current)
    similar_properties = Property.objects.filter(
        property_type=property.property_type,
        is_available=True
    ).exclude(pk=property.pk).order_by('-created_at')[:3]
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
        'title': property.title,
    }
    return render(request, 'housing/property_detail.html', context)

@login_required
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            messages.success(request, 'Property listed successfully!')
            return redirect('housing:property_detail', pk=property.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm()
    
    return render(request, 'housing/property_form.html', {
        'form': form,
        'title': 'List a Property',
        'submit_text': 'List Property',
        'cancel_url': reverse('housing:home')
    })

@login_required
def update_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    # Check ownership
    if property.owner != request.user:
        messages.error(request, 'You do not have permission to edit this property.')
        return redirect('housing:property_detail', pk=property.pk)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully!')
            return redirect('housing:property_detail', pk=property.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'housing/property_form.html', {
        'form': form,
        'title': 'Edit Property',
        'submit_text': 'Update Property',
        'cancel_url': reverse('housing:property_detail', pk=property.pk)
    })

@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    # Check ownership
    if property.owner != request.user:
        messages.error(request, 'You do not have permission to delete this property.')
        return redirect('housing:property_detail', pk=property.pk)
    
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('housing:home')
    
    return render(request, 'housing/property_confirm_delete.html', {
        'property': property,
        'title': 'Delete Property'
    })

@login_required
def my_properties(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    # Filter availability
    availability_filter = request.GET.get('availability')
    if availability_filter == 'available':
        properties = properties.filter(is_available=True)
    elif availability_filter == 'rented':
        properties = properties.filter(is_available=False)
    
    context = {
        'properties': properties,
        'title': 'My Properties',
        'availability_filter': availability_filter,
    }
    return render(request, 'housing/my_properties.html', context)

@login_required
def toggle_availability(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    # Check ownership
    if property.owner != request.user:
        messages.error(request, 'You do not have permission to update this property.')
        return redirect('housing:property_detail', pk=property.pk)
    
    property.is_available = not property.is_available
    property.save()
    
    status = "available" if property.is_available else "rented"
    messages.success(request, f'Property marked as {status}!')
    
    return redirect('housing:property_detail', pk=property.pk)