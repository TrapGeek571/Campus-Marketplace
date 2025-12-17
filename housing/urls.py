# housing/urls.py
from django.urls import path
from . import views

app_name = 'housing'

urlpatterns = [
    # Main pages
    path('', views.housing_home, name='home'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('my-properties/', views.my_properties, name='my_properties'),
    
    # CRUD operations
    path('create/', views.create_property, name='create_property'),
    path('edit/<int:pk>/', views.update_property, name='update_property'),
    path('delete/<int:pk>/', views.delete_property, name='delete_property'),
    
    # Property management
    path('toggle/<int:pk>/', views.toggle_availability, name='toggle_availability'),
    
    # Filter/sort endpoints (optional for AJAX)
    # path('filter/', views.property_filter, name='property_filter'),
    # path('search/', views.property_search, name='property_search'),
]