# food/admin.py - SIMPLIFIED VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, MenuItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'cuisine', 
        'is_verified_display', 
        'created_by'
    ]
    
    list_filter = [
        'cuisine', 
        'is_verified'
    ]
 
    inlines = [MenuItemInline]

    def is_verified_display(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    is_verified_display.short_description = 'Verification'
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(MenuItem)