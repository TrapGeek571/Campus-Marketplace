# marketplace/admin.py (and similar for other apps)
from django.contrib import admin
from .models import Category, Product  # Only your own models

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'is_sold', 'created_at']
    list_filter = ['is_sold', 'category', 'condition']
    search_fields = ['title', 'description']
