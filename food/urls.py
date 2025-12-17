# food/urls.py
from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    # Main pages
    path('', views.food_home, name='home'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('my-restaurants/', views.my_restaurants, name='my_restaurants'),
    
    # Restaurant CRUD operations
    path('create/', views.create_restaurant, name='create_restaurant'),
    path('edit/<int:pk>/', views.update_restaurant, name='update_restaurant'),
    path('delete/<int:pk>/', views.delete_restaurant, name='delete_restaurant'),
    
    # Menu item operations
    path('restaurant/<int:restaurant_id>/menu/add/', views.create_menu_item, name='create_menu_item'),
    path('menu/edit/<int:pk>/', views.update_menu_item, name='update_menu_item'),
    path('menu/delete/<int:pk>/', views.delete_menu_item, name='delete_menu_item'),
    
    # Admin functions
    path('verify/<int:pk>/', views.verify_restaurant, name='verify_restaurant'),
    
    # Additional endpoints (optional)
    # path('cuisine/<str:cuisine_type>/', views.cuisine_list, name='cuisine_list'),
    # path('near-campus/', views.near_campus, name='near_campus'),
]