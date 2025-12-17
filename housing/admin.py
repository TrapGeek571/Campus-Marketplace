from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'rent', 'bedrooms', 'is_furnished', 'is_available', 'owner', 'available_from')
    list_filter = ('property_type', 'is_furnished', 'is_available', 'created_at')
    search_fields = ('title', 'description', 'address', 'owner__username')
    list_editable = ('is_available', 'rent') # Useful for quick updates
    readonly_fields = ('created_at', 'owner')
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'title', 'description', 'property_type')
        }),
        ('Location & Price', {
            'fields': ('address', 'rent')
        }),
        ('Specifications', {
            'fields': ('bedrooms', 'bathrooms', 'is_furnished', 'image')
        }),
        ('Availability', {
            'fields': ('is_available', 'available_from', 'contact_info')
        }),
    )

    # Auto-set the owner in admin
    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

