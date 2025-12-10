from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from accounts.decorators import login_required_message
from .models import Product, Offer
from .forms import ProductForm, OfferForm, ProductFilterForm

@login_required_message
def index(request):
    """Display marketplace products with filtering."""
    form = ProductFilterForm(request.GET)
    
    # Start with all available products
    products = Product.objects.filter(status='available')
    
    # Apply filters if form is valid
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        condition = form.cleaned_data.get('condition')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        negotiable = form.cleaned_data.get('negotiable')
        sort_by = form.cleaned_data.get('sort_by') or 'newest'
        
        # Search filter
        if search:
            products = products.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        
        # Category filter
        if category:
            products = products.filter(category=category)
        
        # Condition filter
        if condition:
            products = products.filter(condition=condition)
        
        # Price filters
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Negotiable filter
        if negotiable == 'yes':
            products = products.filter(negotiable=True)
        elif negotiable == 'no':
            products = products.filter(fixed_price=True)
        
        # Sorting
        if sort_by == 'newest':
            products = products.order_by('-created_at')
        elif sort_by == 'oldest':
            products = products.order_by('created_at')
        elif sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'views':
            products = products.order_by('-views')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Product.objects.filter(status='available').values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'categories': categories,
        'total_products': products.count(),
    }
    return render(request, 'marketplace/index.html', context)

@login_required_message
def create(request):
    """Create a new product listing."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            
            # Set contact info from user profile if not provided
            if not product.contact_email and request.user.email:
                product.contact_email = request.user.email
            if not product.contact_phone and hasattr(request.user, 'profile'):
                product.contact_phone = request.user.profile.phone
            
            product.save()
            messages.success(request, '🎉 Your product has been listed successfully!')
            return redirect('marketplace:detail', pk=product.pk)
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = ProductForm()
    
    return render(request, 'marketplace/create.html', {'form': form})

@login_required_message
def detail(request, pk):
    """View product details."""
    product = get_object_or_404(Product, pk=pk)
    
    # Increment view count (only for logged-in users)
    if request.user != product.seller:
        product.increment_views()
    
    # Check if user has saved this product
    is_saved = request.user in product.saved_by.all()
    
    # Get similar products
    similar_products = Product.objects.filter(
        category=product.category,
        status='available'
    ).exclude(pk=pk).order_by('-created_at')[:4]
    
    # Get user's offers on this product
    user_offers = []
    if request.user.is_authenticated:
        user_offers = Offer.objects.filter(product=product, buyer=request.user).order_by('-created_at')
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'is_saved': is_saved,
        'user_offers': user_offers,
        'offer_form': OfferForm(product=product),
    }
    return render(request, 'marketplace/detail.html', context)

@login_required_message
def edit(request, pk):
    """Edit an existing product listing."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not product.can_edit(request.user):
        messages.error(request, '❌ You do not have permission to edit this product.')
        return redirect('marketplace:detail', pk=product.pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Product updated successfully!')
            return redirect('marketplace:detail', pk=product.pk)
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'marketplace/edit.html', {'form': form, 'product': product})

@login_required_message
def delete(request, pk):
    """Delete a product listing."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not product.can_delete(request.user):
        messages.error(request, '❌ You do not have permission to delete this product.')
        return redirect('marketplace:detail', pk=product.pk)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f'🗑️ Product "{product_title}" has been deleted.')
        return redirect('marketplace:index')
    
    return render(request, 'marketplace/delete.html', {'product': product})

@login_required
def toggle_save(request, pk):
    """Save/unsave a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.user in product.saved_by.all():
        product.saved_by.remove(request.user)
        saved = False
    else:
        product.saved_by.add(request.user)
        saved = True
    
    return JsonResponse({'saved': saved, 'count': product.saved_by.count()})

@login_required
def make_offer(request, pk):
    """Make an offer on a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if not product.negotiable:
        messages.error(request, '❌ This product is not negotiable.')
        return redirect('marketplace:detail', pk=pk)
    
    if request.method == 'POST':
        form = OfferForm(request.POST, product=product)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.product = product
            offer.buyer = request.user
            offer.save()
            
            messages.success(request, f'✅ Your offer of ${offer.amount} has been submitted!')
            return redirect('marketplace:detail', pk=pk)
    
    return redirect('marketplace:detail', pk=pk)

@login_required
def mark_as_sold(request, pk):
    """Mark a product as sold."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not product.can_edit(request.user):
        messages.error(request, '❌ You do not have permission to update this product.')
        return redirect('marketplace:detail', pk=pk)
    
    if request.method == 'POST':
        product.mark_as_sold()
        messages.success(request, '✅ Product marked as sold!')
    
    return redirect('marketplace:detail', pk=pk)

@login_required
def my_listings(request):
    """View user's own listings."""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Stats
    stats = {
        'total': products.count(),
        'available': products.filter(status='available').count(),
        'sold': products.filter(status='sold').count(),
        'pending': products.filter(status='pending').count(),
    }
    
    context = {
        'products': products,
        'stats': stats,
    }
    return render(request, 'marketplace/my_listings.html', context)

@login_required
def saved_items(request):
    """View user's saved items."""
    saved_products = request.user.saved_products.filter(status='available').order_by('-saved_by')
    
    context = {
        'saved_products': saved_products,
    }
    return render(request, 'marketplace/saved_items.html', context)

def category_view(request, category):
    """View products by category."""
    products = Product.objects.filter(category=category, status='available').order_by('-created_at')
    
    # Get category display name
    category_name = dict(Product.CATEGORY_CHOICES).get(category, category)
    
    context = {
        'products': products,
        'category': category,
        'category_name': category_name,
    }
    return render(request, 'marketplace/category.html', context)