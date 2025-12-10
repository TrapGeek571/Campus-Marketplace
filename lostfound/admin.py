from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import LostItem

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'item_type', 'category', 'user', 'status', 'created_at', 'view_links')
    list_filter = ('item_type', 'category', 'status', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'contact_email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    # Define custom admin actions (for bulk operations)
    actions = ['mark_as_returned', 'mark_as_lost']
    
    fieldsets = (
        ('Item Details', {
            'fields': ('user', 'title', 'description', 'item_type', 'category', 'image')
        }),
        ('Location & Dates', {
            'fields': ('location_lost', 'location_found', 'date_lost', 'date_found')
        }),
        ('Contact & Status', {
            'fields': ('contact_email', 'contact_phone', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def view_links(self, obj):
        """Display view and edit links in admin list."""
        view_url = reverse('lostfound:detail', kwargs={'pk': obj.pk})
        edit_url = reverse('lostfound:edit', kwargs={'pk': obj.pk})
        return format_html(
            '<a href="{}" class="btn btn-sm btn-info" target="_blank">View</a> '
            '<a href="{}" class="btn btn-sm btn-warning" target="_blank">Edit</a>',
            view_url, edit_url
        )
    view_links.short_description = 'Actions'
    view_links.allow_tags = True
    
    def mark_as_returned(self, request, queryset):
        """Admin action to mark items as returned."""
        updated = queryset.update(status='returned')
        self.message_user(request, f'{updated} item(s) marked as returned.')
    mark_as_returned.short_description = "Mark selected items as returned"
    
    def mark_as_lost(self, request, queryset):
        """Admin action to mark items as lost."""
        updated = queryset.update(status='lost')
        self.message_user(request, f'{updated} item(s) marked as lost.')
    mark_as_lost.short_description = "Mark selected items as lost"