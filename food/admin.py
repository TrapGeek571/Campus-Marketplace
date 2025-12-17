from django.contrib import admin
from .models import Restaurant, MenuItem

class MenuItemInline(admin.TabularInline): # Shows menu items inside the Restaurant admin page
    model = MenuItem
    extra = 1 # Shows 1 empty form by default
    fields = ('name', 'description', 'price', 'is_available')

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'address', 'is_verified', 'created_by', 'created_at')
    list_filter = ('cuisine', 'is_verified', 'created_at')
    search_fields = ('name', 'description', 'address', 'created_by__username')
    list_editable = ('is_verified',)
    readonly_fields = ('created_at', 'created_by')
    inlines = [MenuItemInline] # Embed the menu item form here
    fieldsets = (
        ('Restaurant Info', {
            'fields': ('created_by', 'name', 'description', 'cuisine', 'image')
        }),
        ('Contact & Hours', {
            'fields': ('address', 'phone', 'opening_hours')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'is_available')
    list_filter = ('is_available', 'restaurant')
    search_fields = ('name', 'description', 'restaurant__name')
