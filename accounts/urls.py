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
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Additional account URLs (you can add these later)
    # path('password-change/', views.password_change_view, name='password_change'),
    # path('password-reset/', views.password_reset_view, name='password_reset'),
    # path('verify-email/', views.verify_email_view, name='verify_email'),
]