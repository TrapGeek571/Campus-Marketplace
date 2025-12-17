# marketplace/urls.py
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main pages
    path('', views.marketplace_home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('my-products/', views.my_products, name='my_products'),
    
    # CRUD operations
    path('create/', views.create_product, name='create_product'),
    path('edit/<int:pk>/', views.update_product, name='update_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    
    # Product management
    path('sold/<int:pk>/', views.mark_as_sold, name='mark_as_sold'),
    
    # Filter endpoints (optional for AJAX)
    # path('category/<int:category_id>/', views.category_products, name='category_products'),
    # path('search/', views.product_search, name='product_search'),
]