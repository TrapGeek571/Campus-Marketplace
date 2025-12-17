# accounts/admin.py - FIXED VERSION
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'student_id', 'phone_number', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'student_id', 'phone_number', 'profile_picture')}),
    )

# Unregister if already registered to avoid duplicate
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

# Register the model
admin.site.register(CustomUser, CustomUserAdmin)