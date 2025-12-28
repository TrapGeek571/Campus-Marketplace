from django.contrib import admin
from django.utils.html import format_html
from .models import Property

class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'owner', 
        'property_type', 
        'rent', 
        'is_available_display', 
        'created_at'
    ]

    list_filter = [
        'property_type', 
        'is_available', 
        'is_furnished'
    ]

    search_fields = [
        'title', 
        'description', 
        'address'
    ]
    def is_available_display(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Rented</span>')
    is_available_display.short_description = 'Status'
admin.site.register(Property, PropertyAdmin)