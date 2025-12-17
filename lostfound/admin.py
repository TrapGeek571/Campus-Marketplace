from django.contrib import admin
from .models import LostItem

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_type', 'status', 'location', 'user', 'date_lost', 'created_at')
    list_filter = ('status', 'item_type', 'date_lost', 'created_at')
    search_fields = ('item_name', 'description', 'location', 'user__username')
    list_editable = ('status',) # Allows you to change status directly from the list view
    readonly_fields = ('created_at', 'user')
    fieldsets = (
        (None, {
            'fields': ('user', 'item_name', 'description')
        }),
        ('Details', {
            'fields': ('item_type', 'status', 'location', 'date_lost', 'image', 'contact_info')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',) # This section is collapsible
        }),
    )

    # Automatically set the user when saving from admin (if not set)
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)