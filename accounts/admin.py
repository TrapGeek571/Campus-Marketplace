# accounts/admin.py - FIXED VERSION
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'student_id']
    ordering = ['-date_joined']
    actions = ['ban_users', 'activate_users', 'make_staff', 'remove_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'student_id', 'phone_number', 'profile_picture')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'student_id', 'phone_number', 'profile_picture')}),
    )
    
    def ban_users(self, request, queryset):
        """Ban selected users"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users have been banned.')
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users have been activated.')
    
    def make_staff(self, request, queryset):
        """Make selected users staff"""
        count = queryset.update(is_staff=True)
        self.message_user(request, f'{count} users have been made staff members.')
    
    def remove_staff(self, request, queryset):
        """Remove staff status from selected users"""
        # Don't allow removing staff from superusers
        non_superusers = queryset.filter(is_superuser=False)
        count = non_superusers.update(is_staff=False)
        self.message_user(request, f'Staff status removed from {count} users.')
    
    ban_users.short_description = "Ban selected users"
    activate_users.short_description = "Activate selected users"
    make_staff.short_description = "Make selected users staff"
    remove_staff.short_description = "Remove staff status"

# Unregister if already registered to avoid duplicate
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

# Register the model
admin.site.register(CustomUser, CustomUserAdmin)