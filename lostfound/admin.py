from django.contrib import admin
from django.utils.html import format_html
from .models import LostFoundItem

@admin.register(LostFoundItem)
class LostFoundItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'category', 'status_badge', 'location', 'user', 'date_lost', 'created_at', 'image_preview', 'status')
    list_filter = ('status', 'category', 'date_lost', 'created_at')
    search_fields = ('item_name', 'description', 'location', 'user__username')
    list_editable = ('status',) # Allows you to change status directly from the list view
    readonly_fields = ('created_at', 'user')
    actions = ['mark_as_returned', 'mark_as_found', 'delete_inappropriate']
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
        
    def status_badge(self, obj):
        colors = {'lost': 'danger', 'found': 'success', 'returned': 'info'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return format_html('<span class="text-muted">No image</span>')
    image_preview.short_description = 'Preview'
    
    def mark_as_returned(self, request, queryset):
        queryset.update(status='returned')
        self.message_user(request, f'{queryset.count()} items marked as returned.')
    
    def mark_as_found(self, request, queryset):
        queryset.update(status='found')
        self.message_user(request, f'{queryset.count()} items marked as found.')
    
    def delete_inappropriate(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} inappropriate items deleted.')
    
    mark_as_returned.short_description = "Mark selected as returned"
    mark_as_found.short_description = "Mark selected as found"
    delete_inappropriate.short_description = "Delete inappropriate content"    
        
    