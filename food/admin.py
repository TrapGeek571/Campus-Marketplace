# food/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import FoodVendor, MenuItem, FoodReview

class MenuItemInline(admin.TabularInline):
    """Inline admin for menu items"""
    model = MenuItem
    extra = 1
    fields = ['name', 'category', 'price', 'is_available', 'is_popular']
    ordering = ['category', 'name']


class FoodReviewInline(admin.TabularInline):
    """Inline admin for food reviews"""
    model = FoodReview
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = False
    max_num = 5


@admin.register(FoodVendor)
class FoodVendorAdmin(admin.ModelAdmin):
    """Admin interface for FoodVendor model"""
    list_display = [
        'name', 
        'vendor_type', 
        'cuisine_type', 
        'city', 
        'is_active', 
        'is_verified',
        'is_featured',
        'views_count',
        'created_at'
    ]
    
    list_filter = [
        'vendor_type',
        'cuisine_type', 
        'city',
        'is_active', 
        'is_verified',
        'is_featured',
        'delivery_available',
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'address', 
        'city', 
        'neighborhood',
        'description'
    ]
    
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'vendor_type', 'name', 'description', 'cuisine_type'
            )
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'neighborhood', 'latitude', 'longitude'
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone', 'email', 'website'
            )
        }),
        ('Operating Hours', {
            'fields': (
                'opening_time', 'closing_time'
            )
        }),
        ('Features & Services', {
            'fields': (
                'delivery_available', 
                'takeaway_available', 
                'dine_in_available',
                'accepts_card', 
                'wifi_available'
            )
        }),
        ('Images', {
            'fields': (
                'main_image', 
                'image_2', 
                'image_3'
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 
                'is_verified', 
                'is_featured',
                'views_count'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MenuItemInline, FoodReviewInline]
    
    def get_form(self, request, obj=None, **kwargs):
        """Set user to current user when creating new vendor"""
        form = super().get_form(request, obj, **kwargs)
        if 'user' in form.base_fields and obj is None:
            form.base_fields['user'].initial = request.user
        return form


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin interface for MenuItem model"""
    list_display = [
        'name', 
        'vendor', 
        'category', 
        'price', 
        'is_available',
        'is_popular'
    ]
    
    list_filter = [
        'category',
        'is_available',
        'is_popular',
        'vendor__name'
    ]
    
    search_fields = [
        'name', 
        'description', 
        'vendor__name'
    ]
    
    list_editable = ['price', 'is_available', 'is_popular']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'vendor', 'name', 'description', 'category', 'price'
            )
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': (
                'is_available', 
                'is_popular'
            )
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter vendors in dropdown"""
        if db_field.name == "vendor":
            kwargs["queryset"] = FoodVendor.objects.filter(is_active=True).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FoodReview)
class FoodReviewAdmin(admin.ModelAdmin):
    """Admin interface for FoodReview model"""
    list_display = [
        'vendor', 
        'user', 
        'rating_display', 
        'created_at',
        'truncated_comment'
    ]
    
    list_filter = [
        'rating',
        'vendor__name',
        'created_at'
    ]
    
    search_fields = [
        'comment', 
        'vendor__name', 
        'user__username',
        'user__email'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': (
                'vendor', 'user', 'rating', 'comment'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Display stars for rating"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(f'<span style="color: #f39c12; font-size: 14px;">{stars}</span>')
    rating_display.short_description = 'Rating'
    
    def truncated_comment(self, obj):
        """Display truncated comment"""
        if len(obj.comment) > 50:
            return f"{obj.comment[:50]}..."
        return obj.comment
    truncated_comment.short_description = 'Comment'
    
    def has_add_permission(self, request):
        """Prevent adding reviews from admin - should be done via frontend"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow changing reviews? Maybe not, but for admin we can"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting reviews"""
        return True