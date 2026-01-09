from django.contrib import admin
from django.utils.html import format_html
from .models import HousingListing, FavoriteListing

@admin.register(HousingListing)
class HousingListingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'listing_type_display', 'property_type_display', 
        'city', 'price_display_admin', 'bedrooms', 'is_available', 
        'views_count', 'created_at', 'image_preview', 'is_featured'
    ]
    
    list_filter = ['listing_type', 'property_type', 'city', 'is_available', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'address', 'city', 'user__username', 'contact_name', 'contact_phone']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'image_preview_large']
    list_editable = ['is_available', 'is_featured']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'listing_type', 'property_type', 'title', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city', 'neighborhood')
        }),
        ('Pricing', {
            'fields': ('price', 'price_period', 'deposit', 'utilities_included')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_meters', 'furnished', 'available_from', 'lease_duration', 'amenities')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_phone', 'contact_email', 'contact_preference')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4', 'image_preview_large')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured', 'views_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def listing_type_display(self, obj):
        return obj.get_listing_type_display()
    listing_type_display.short_description = 'Type'
    
    def property_type_display(self, obj):
        return obj.get_property_type_display()
    property_type_display.short_description = 'Property'
    
    def price_display_admin(self, obj):
        return obj.price_display
    price_display_admin.short_description = 'Price'
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.main_image.build_url(width=50, height=50, crop="fill")
            )
        return "No image"
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        images = []
        image_fields = ['main_image', 'image_2', 'image_3', 'image_4']
        
        for field_name in image_fields:
            image = getattr(obj, field_name)
            if image:
                images.append(
                    format_html(
                        '<div style="margin-bottom: 10px;">'
                        '<strong>{}:</strong><br>'
                        '<img src="{}" width="300" style="border-radius: 8px; margin-top: 5px;" />'
                        '</div>',
                        field_name.replace('_', ' ').title(),
                        image.url
                    )
                )
        
        if images:
            return format_html(''.join(images))
        return "No images uploaded"
    image_preview_large.short_description = 'Image Preview'
    image_preview_large.allow_tags = True

@admin.register(FavoriteListing)
class FavoriteListingAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'listing__title']
    date_hierarchy = 'created_at'