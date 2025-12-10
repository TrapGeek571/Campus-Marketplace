from django.contrib import admin
from .models import Product, Offer, ProductImage

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'condition', 'price', 'status', 'views', 'created_at')
    list_filter = ('category', 'condition', 'status', 'negotiable', 'created_at')
    search_fields = ('title', 'description', 'seller__username', 'brand', 'model')
    readonly_fields = ('views', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'title', 'description', 'category', 'condition')
        }),
        ('Pricing', {
            'fields': ('price', 'negotiable', 'fixed_price', 'original_price')
        }),
        ('Images', {
            'fields': ('image1', 'image2', 'image3', 'image4')
        }),
        ('Details', {
            'fields': ('brand', 'model', 'warranty_remaining', 'purchase_date')
        }),
        ('Contact & Location', {
            'fields': ('contact_phone', 'contact_email', 'location', 'meetup_preference')
        }),
        ('Status & Metrics', {
            'fields': ('status', 'sold_at', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__title', 'buyer__username', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
admin.site.register(ProductImage)
