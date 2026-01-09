from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import HousingListing, FavoriteListing
from .forms import HousingListingForm, HousingSearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView

class HousingCreateView(LoginRequiredMixin, CreateView):
    model = HousingListing
    form_class = HousingListingForm
    template_name = 'housing/listing_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class HousingUpdateView(LoginRequiredMixin, UpdateView):
    model = HousingListing
    form_class = HousingListingForm
    template_name = 'housing/listing_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

def housing_home(request):
    """Home page showing all housing listings"""
    form = HousingSearchForm(request.GET or None)
    listings = HousingListing.objects.filter(is_available=True)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        listing_type = form.cleaned_data.get('listing_type')
        property_type = form.cleaned_data.get('property_type')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')
        furnished = form.cleaned_data.get('furnished')
        utilities_included = form.cleaned_data.get('utilities_included')
        sort_by = form.cleaned_data.get('sort_by', 'newest')
        
        # Apply filters
        if search:
            listings = listings.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search) |
                Q(neighborhood__icontains=search) |
                Q(city__icontains=search)
            )
        
        if listing_type:
            listings = listings.filter(listing_type=listing_type)
        
        if property_type:
            listings = listings.filter(property_type=property_type)
        
        if city:
            listings = listings.filter(city__icontains=city)
        
        if min_price is not None:
            listings = listings.filter(price__gte=min_price)
        
        if max_price is not None:
            listings = listings.filter(price__lte=max_price)
        
        if bedrooms is not None:
            listings = listings.filter(bedrooms=bedrooms)
        
        if furnished:
            listings = listings.filter(furnished=furnished)
        
        if utilities_included == 'yes':
            listings = listings.filter(utilities_included=True)
        elif utilities_included == 'no':
            listings = listings.filter(utilities_included=False)
        
        # Apply sorting
        if sort_by == 'newest':
            listings = listings.order_by('-created_at')
        elif sort_by == 'price_low':
            listings = listings.order_by('price')
        elif sort_by == 'price_high':
            listings = listings.order_by('-price')
        elif sort_by == 'bedrooms':
            listings = listings.order_by('-bedrooms')
    
    # Get featured listings (first 3)
    featured_listings = listings.filter(is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(listings, 12)  # 12 listings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get cities for filter (distinct cities with listings)
    cities = HousingListing.objects.filter(is_available=True).values_list('city', flat=True).distinct()
    
    context = {
        'listings': page_obj,
        'featured_listings': featured_listings,
        'form': form,
        'cities': sorted(cities),
        'total_listings': listings.count(),
    }
    return render(request, 'housing/home.html', context)

def listing_detail(request, pk):
    """View details of a housing listing"""
    listing = get_object_or_404(HousingListing, pk=pk)
    
    # Increment view count
    listing.increment_views()
    
    # Check if user has favorited this listing
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = FavoriteListing.objects.filter(
            user=request.user, listing=listing
        ).exists()
    
    # Get similar listings (same city and property type)
    similar_listings = HousingListing.objects.filter(
        city=listing.city,
        property_type=listing.property_type,
        is_available=True
    ).exclude(pk=listing.pk).order_by('-created_at')[:4]
    
    context = {
        'listing': listing,
        'is_favorited': is_favorited,
        'similar_listings': similar_listings,
        'amenities_list': listing.get_amenities_list(),
    }
    return render(request, 'housing/listing_detail.html', context)

@login_required
def create_listing(request):
    """Create a new housing listing"""
    if request.method == 'POST':
        form = HousingListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            
            messages.success(request, 'Your housing listing has been created successfully!')
            return redirect('housing:listing_detail', pk=listing.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousingListingForm()
    
    context = {
        'form': form,
        'title': 'Create Housing Listing',
    }
    return render(request, 'housing/listing_form.html', context)

@login_required
def update_listing(request, pk):
    """Update an existing housing listing"""
    listing = get_object_or_404(HousingListing, pk=pk)
    
    # Check ownership
    if listing.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this listing.')
        return redirect('housing:listing_detail', pk=listing.pk)
    
    if request.method == 'POST':
        form = HousingListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('housing:listing_detail', pk=listing.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousingListingForm(instance=listing)
    
    context = {
        'form': form,
        'listing': listing,
        'title': 'Update Listing',
    }
    return render(request, 'housing/listing_form.html', context)

@login_required
def delete_listing(request, pk):
    """Delete a housing listing"""
    listing = get_object_or_404(HousingListing, pk=pk)
    
    # Check ownership
    if listing.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this listing.')
        return redirect('housing:listing_detail', pk=listing.pk)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted successfully!')
        return redirect('housing:home')
    
    context = {
        'listing': listing,
    }
    return render(request, 'housing/confirm_delete.html', context)

@login_required
def my_listings(request):
    """View user's own housing listings"""
    listings = HousingListing.objects.filter(user=request.user).order_by('-created_at')
    
    # Get stats
    total_listings = listings.count()
    active_listings = listings.filter(is_available=True).count()
    total_views = listings.aggregate(total_views=Count('views_count'))['total_views'] or 0
    
    context = {
        'listings': listings,
        'total_listings': total_listings,
        'active_listings': active_listings,
        'total_views': total_views,
    }
    return render(request, 'housing/my_listings.html', context)

@login_required
def toggle_favorite(request, pk):
    """Add/remove listing from favorites"""
    listing = get_object_or_404(HousingListing, pk=pk)
    
    favorite, created = FavoriteListing.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if not created:
        # If already exists, remove it (unfavorite)
        favorite.delete()
        messages.success(request, 'Removed from favorites.')
    else:
        messages.success(request, 'Added to favorites!')
    
    return redirect('housing:listing_detail', pk=listing.pk)

@login_required
def my_favorites(request):
    """View user's favorite listings"""
    favorites = FavoriteListing.objects.filter(user=request.user).select_related('listing')
    listings = [fav.listing for fav in favorites]
    
    context = {
        'listings': listings,
        'favorites_count': len(listings),
    }
    return render(request, 'housing/my_favorites.html', context)

def cities_list(request):
    """View housing listings by city"""
    # Get all cities with available listings
    cities = HousingListing.objects.filter(
        is_available=True
    ).values('city').annotate(
        listing_count=Count('id')
    ).order_by('city')
    
    context = {
        'cities': cities,
    }
    return render(request, 'housing/cities.html', context)

def city_listings(request, city):
    """View to show all listings in a specific city"""
    # Fix: Use HousingListing directly instead of models.HousingListing
    listings = HousingListing.objects.filter(
        city__iexact=city,  # Case-insensitive match
        is_available=True
    ).order_by('-created_at')
    
    # Get distinct neighborhoods in this city
    neighborhoods = HousingListing.objects.filter(
        city__iexact=city,
        is_available=True,
        neighborhood__isnull=False
    ).values_list('neighborhood', flat=True).distinct()
    
    # Apply search filters if any
    search_form = HousingSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        listing_type = search_form.cleaned_data.get('listing_type')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        furnished = search_form.cleaned_data.get('furnished')
        utilities_included = search_form.cleaned_data.get('utilities_included')
        sort_by = search_form.cleaned_data.get('sort_by', 'newest')
        
        # Apply filters
        if search_query:
            listings = listings.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(neighborhood__icontains=search_query)
            )
        
        if listing_type:
            listings = listings.filter(listing_type=listing_type)
        
        if property_type:
            listings = listings.filter(property_type=property_type)
        
        if min_price:
            listings = listings.filter(price__gte=min_price)
        
        if max_price:
            listings = listings.filter(price__lte=max_price)
        
        if bedrooms:
            listings = listings.filter(bedrooms=bedrooms)
        
        if furnished:
            listings = listings.filter(furnished=furnished)
        
        if utilities_included == 'yes':
            listings = listings.filter(utilities_included=True)
        elif utilities_included == 'no':
            listings = listings.filter(utilities_included=False)
        
        # Apply sorting
        if sort_by == 'price_low':
            listings = listings.order_by('price')
        elif sort_by == 'price_high':
            listings = listings.order_by('-price')
        elif sort_by == 'bedrooms':
            listings = listings.order_by('-bedrooms')
        else:  # newest
            listings = listings.order_by('-created_at')
    
    context = {
        'listings': listings,
        'city': city,
        'neighborhoods': neighborhoods,
        'search_form': search_form,
        'total_listings': listings.count(),
    }
    
    return render(request, 'housing/city_listings.html', context)