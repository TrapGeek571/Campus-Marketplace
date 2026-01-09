# food/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import FoodVendor, MenuItem, FoodReview
from .forms import FoodVendorForm, MenuItemForm, FoodReviewForm, FoodSearchForm
from django.urls import reverse_lazy

class MyRestaurantsView(LoginRequiredMixin, ListView):
    """View for user to see their own restaurants"""
    model = FoodVendor
    template_name = 'food/my_restaurants.html'
    context_object_name = 'restaurants'
    
    def get_queryset(self):
        return FoodVendor.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

def home(request):
    """Food app homepage"""
    featured_vendors = FoodVendor.objects.filter(
        is_featured=True, 
        is_active=True
    )[:6]
    
    context = {
        'featured_vendors': featured_vendors,
        'cuisine_choices': FoodVendor.CUISINE_CHOICES,
        'vendor_type_choices': FoodVendor.VENDOR_TYPE_CHOICES,
    }
    return render(request, 'food/home.html', context)


class FoodVendorListView(ListView):
    model = FoodVendor
    template_name = 'food/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FoodVendor.objects.filter(is_active=True)
        
        # Get search parameters
        search = self.request.GET.get('search')
        cuisine_type = self.request.GET.get('cuisine_type')
        vendor_type = self.request.GET.get('vendor_type')
        delivery_available = self.request.GET.get('delivery_available')
        city = self.request.GET.get('city')
        sort_by = self.request.GET.get('sort_by', 'newest')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(cuisine_type__icontains=search) |
                Q(address__icontains=search)
            )
        
        if cuisine_type:
            queryset = queryset.filter(cuisine_type=cuisine_type)
        
        if vendor_type:
            queryset = queryset.filter(vendor_type=vendor_type)
        
        if delivery_available == 'yes':
            queryset = queryset.filter(delivery_available=True)
        elif delivery_available == 'no':
            queryset = queryset.filter(delivery_available=False)
        
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        # Apply sorting
        if sort_by == 'rating':
            # Annotate with average rating
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views_count')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = FoodSearchForm(self.request.GET)
        return context


class FoodVendorDetailView(DetailView):
    model = FoodVendor
    template_name = 'food/vendor_detail.html'
    context_object_name = 'vendor'
    
    def get_object(self):
        obj = super().get_object()
        obj.increment_views()  # Increment view count
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.get_object()
        
        # Get menu items
        menu_items = vendor.menu_items.filter(is_available=True)
        
        # Get reviews
        reviews = vendor.reviews.all().order_by('-created_at')
        
        # Calculate average rating
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            context['avg_rating'] = round(avg_rating, 1)
        else:
            context['avg_rating'] = 0
            
        # Check if user has already reviewed
        user_review = None
        if self.request.user.is_authenticated:
            user_review = vendor.reviews.filter(user=self.request.user).first()    
        
        # Add review form
        if self.request.user.is_authenticated:
            if user_review:
                # User already reviewed, pre-fill form
                context['review_form'] = FoodReviewForm(instance=user_review)
                context['user_has_reviewed'] = True
                context['user_review'] = user_review
            else:
                # New review form
                context['review_form'] = FoodReviewForm()
                context['user_has_reviewed'] = False
        
        context.update({
            'menu_items': menu_items,
            'reviews': reviews,
            'similar_vendors': FoodVendor.objects.filter(
                cuisine_type=vendor.cuisine_type,
                is_active=True
            ).exclude(pk=vendor.pk)[:4]
        })
        
        return context


class FoodVendorCreateView(LoginRequiredMixin, CreateView):
    model = FoodVendor
    form_class = FoodVendorForm
    template_name = 'food/vendor_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Restaurant listed successfully!')
        return super().form_valid(form)


class FoodVendorUpdateView(LoginRequiredMixin, UpdateView):
    model = FoodVendor
    form_class = FoodVendorForm
    template_name = 'food/vendor_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            messages.error(request, "You don't have permission to edit this listing.")
            return redirect('food:vendor_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Restaurant updated successfully!')
        return super().form_valid(form)
    
@login_required
def add_review(request, vendor_pk):
    """Add a review for a food vendor"""
    vendor = get_object_or_404(FoodVendor, pk=vendor_pk, is_active=True)
    
    # Check if user already reviewed this vendor
    existing_review = FoodReview.objects.filter(vendor=vendor, user=request.user).first()
    
    if request.method == 'POST':
        if existing_review:
            # Update existing review
            form = FoodReviewForm(request.POST, instance=existing_review)
            message = "Review updated successfully!"
        else:
            # Create new review
            form = FoodReviewForm(request.POST)
            message = "Review added successfully!"
        
        if form.is_valid():
            review = form.save(commit=False)
            review.vendor = vendor
            review.user = request.user
            review.save()
            messages.success(request, message)
        else:
            messages.error(request, "Please correct the errors below.")
    
    return redirect('food:vendor_detail', pk=vendor_pk)

class FoodVendorDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a food vendor"""
    model = FoodVendor
    template_name = 'food/vendor_confirm_delete.html'
    success_url = reverse_lazy('food:my_restaurants')
    context_object_name = 'vendor'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            messages.error(request, "You don't have permission to delete this listing.")
            return redirect('food:vendor_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Restaurant deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
class MenuItemCreateView(LoginRequiredMixin, CreateView):
    """View for adding a menu item to a restaurant"""
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'food/menu_item_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Get the vendor from URL parameter
        self.vendor = get_object_or_404(FoodVendor, pk=kwargs['vendor_pk'])
        
        # Check if user owns the vendor
        if self.vendor.user != request.user:
            messages.error(request, "You can only add menu items to your own restaurant.")
            return redirect('food:vendor_detail', pk=self.vendor.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.vendor
        context['title'] = f"Add Menu Item - {self.vendor.name}"
        return context
    
    def form_valid(self, form):
        form.instance.vendor = self.vendor
        messages.success(self.request, 'Menu item added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return redirect('food:vendor_detail', kwargs={'pk': self.vendor.pk})


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a menu item"""
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'food/menu_item_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        
        # Check if user owns the vendor
        if obj.vendor.user != request.user:
            messages.error(request, "You can only edit menu items for your own restaurant.")
            return redirect('food:vendor_detail', pk=obj.vendor.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.object.vendor
        context['title'] = f"Edit Menu Item - {self.object.vendor.name}"
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Menu item updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('food:vendor_detail', kwargs={'pk': self.object.vendor.pk})


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a menu item"""
    model = MenuItem
    template_name = 'food/menu_item_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        
        # Check if user owns the vendor
        if obj.vendor.user != request.user:
            messages.error(request, "You can only delete menu items from your own restaurant.")
            return redirect('food:vendor_detail', pk=obj.vendor.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.object.vendor
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Menu item deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('food:vendor_detail', kwargs={'pk': self.object.vendor.pk})
    
class RestaurantMenuManagementView(LoginRequiredMixin, DetailView):
    """View for restaurant owners to manage all menu items"""
    model = FoodVendor
    template_name = 'food/menu_management.html'
    context_object_name = 'vendor'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            messages.error(request, "You can only manage menu items for your own restaurant.")
            return redirect('food:vendor_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_items'] = self.object.menu_items.all().order_by('category', 'name')
        context['categories'] = dict(MenuItem.CATEGORY_CHOICES)
        return context    