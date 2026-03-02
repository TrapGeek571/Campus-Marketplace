# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm
from accounts.models import SellerProfile

@login_required
def marketplace_home(request):
    products = Product.objects.filter(is_sold=False).order_by('-created_at')
    categories = Category.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(seller__username__icontains=search_query)
        )
    
    # Filter by condition
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    context = {
        'products': products,
        'categories': categories,
        'title': 'Marketplace',
        'search_query': search_query or '',
        'selected_category': category_id,
    }
    return render(request, 'marketplace/home.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Get related products (same category, excluding current)
    related_products = Product.objects.filter(
        category=product.category,
        is_sold=False
    ).exclude(pk=product.pk).order_by('-created_at')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'title': product.title,
    }
    return render(request, 'marketplace/product_detail.html', context)

@login_required
def create_product(request):
    seller_profile, created = SellerProfile.objects.get_or_create(user=request.user)
    if not seller_profile.can_post_more_listings():
        messages.error(request, 'You have reached your maximum active listings. Become a verified seller to post more.')
        return redirect('marketplace:my_listings')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product listed successfully!')
            return redirect('marketplace:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    return render(request, 'marketplace/product_form.html', {
        'form': form,
        'title': 'Sell an Item',
        'submit_text': 'List Item',
        'cancel_url': reverse('marketplace:home')
    })

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    # Check ownership
    if product.seller != request.user:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('marketplace:product_detail', product_id=product.pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated_product = form.save(commit=False)
            updated_product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('marketplace:product_detail', product_id=updated_product.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'marketplace/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'submit_text': 'Update Product',
        'cancel_url': reverse('marketplace:product_detail', args=[product.pk])
    })

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    # Check ownership
    if product.seller != request.user:
        messages.error(request, 'You do not have permission to delete this product.')
        return redirect('marketplace:product_detail', product_id=product.pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('marketplace:my_listings')
    
    return render(request, 'marketplace/product_confirm_delete.html', {
        'product': product,
        'title': 'Delete Product'
    })

@login_required
def my_products(request):
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter sold/unsold
    filter_type = request.GET.get('filter')
    if filter_type == 'sold':
        products = products.filter(is_sold=True)
    elif filter_type == 'unsold':
        products = products.filter(is_sold=False)
    
    context = {
        'products': products,
        'title': 'My Products',
        'filter_type': filter_type,
    }
    return render(request, 'marketplace/my_products.html', context)

def categories_list(request):
    """Display all categories"""
    categories = Category.objects.all()
    return render(request, 'marketplace/categories.html', {
        'categories': categories
    })

@login_required
def my_listings(request):
    """Display user's own listings"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {
        'products': products,
        'categories': Category.objects.all()
    })
  
@login_required
def favorites_list(request):
    """Display user's favorite products"""
    # We'll implement this properly later
    return render(request, 'marketplace/favorites.html', {
        'categories': Category.objects.all()
    })    

@login_required
def category_view(request, category_name):
    # Get the category or return 404
    category = get_object_or_404(Category, name__iexact=category_name)
    
    # Get products in this category
    products = Product.objects.filter(
        category=category,
        is_sold=False
    ).order_by('-created_at')
    
    # Apply search filter if provided
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply price filter if provided
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    context = {
        'category': category,
        'products': products,
        'search_query': search_query,
        'categories': Category.objects.all(),  # For dropdowns
    }
    
    return render(request, 'marketplace/category.html', context)

@login_required
def mark_as_sold(request, pk):
    product = get_object_or_404(Product, id=pk, seller=request.user)
    
    # Check ownership
    if product.seller != request.user:
        messages.error(request, 'You do not have permission to update this product.')
        return redirect('marketplace:product_detail', pk=product.pk)
    
    product.is_sold = True
    product.save()
    messages.success(request, 'Product marked as sold!')
    return redirect('marketplace:product_detail', pk=product.pk)

@login_required
def seller_store(request, username):
    seller = get_object_or_404(User, username=username)
    seller_profile = seller.seller_profile
    products = Product.objects.filter(
        seller=seller, 
        is_sold=False, 
        expired=False
    ).order_by('-created_at')
    
    return render(request, 'marketplace/seller_store.html', {
        'seller': seller,
        'seller_profile': seller_profile,
        'products': products
    })