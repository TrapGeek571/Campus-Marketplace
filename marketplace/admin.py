# marketplace/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'is_sold', 'created_at', 'status_badge', 'image_preview']
    list_filter = ['is_sold', 'category', 'condition', 'created_at']
    search_fields = ['title', 'description', 'seller__username']
    list_editable = ['is_sold']
    actions = ['mark_as_sold', 'mark_as_available', 'delete_selected']
    
    def status_badge(self, obj):
        color = 'danger' if obj.is_sold else 'success'
        text = 'Sold' if obj.is_sold else 'Available'
        return format_html('<span class="badge bg-{}">{}</span>', color, text)
    status_badge.short_description = 'Status'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return format_html('<span class="text-muted">No image</span>')
    image_preview.short_description = 'Preview'
    
    def mark_as_sold(self, request, queryset):
        queryset.update(is_sold=True)
        self.message_user(request, f'{queryset.count()} products marked as sold.')
    
    def mark_as_available(self, request, queryset):
        queryset.update(is_sold=False)
        self.message_user(request, f'{queryset.count()} products marked as available.')
    
    mark_as_sold.short_description = "Mark selected as sold"
    mark_as_available.short_description = "Mark selected as available"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'

admin.site.register(Product, ProductAdmin)