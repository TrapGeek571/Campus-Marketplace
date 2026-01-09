# lostfound/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import LostFoundItem

@admin.register(LostFoundItem)
class LostFoundItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'status_display', 'user', 'location', 'date_lost', 'created_at', 'image_preview']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['item_name', 'description', 'location', 'user__username', 'contact_info']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Item Information', {
            'fields': ('user', 'category', 'item_name', 'description', 'status')
        }),
        ('Location & Contact', {
            'fields': ('location', 'contact_info')
        }),
        ('Date & Image', {
            'fields': ('date_lost', 'image', 'image_preview_large')
        }),
        ('Status', {
            'fields': ('is_resolved',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'lost': 'danger',
            'found': 'success',
            'returned': 'info'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.build_url(width=50, height=50, crop="fill")
            )
        return "No image"
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="border-radius: 8px; margin-top: 10px;" />',
                obj.image.build_url(width=300, crop="fill")
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Image Preview'
    image_preview_large.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)