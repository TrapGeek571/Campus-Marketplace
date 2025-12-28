# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/delete-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/users/', views.admin_users_api, name='admin_users_api'),
    path('api/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Additional account URLs (you can add these later)
    # path('password-change/', views.password_change_view, name='password_change'),
    # path('password-reset/', views.password_reset_view, name='password_reset'),
    # path('verify-email/', views.verify_email_view, name='verify_email'),
]