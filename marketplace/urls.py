# marketplace/urls.py
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main pages
    path('', views.marketplace_home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('my-products/', views.my_products, name='my_products'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('categories/', views.categories_list, name='categories'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('store/<str:username>/', views.seller_store, name='seller_store'),
    
    # CRUD operations
    path('create/', views.create_product, name='create_product'),
    path('edit/<int:product_id>/', views.update_product, name='update_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Product management
    path('sold/<int:product_id>/', views.mark_as_sold, name='mark_as_sold'),
    
    # Filter endpoints (optional for AJAX)
    # path('category/<int:category_id>/', views.category_products, name='category_products'),
    # path('search/', views.product_search, name='product_search'),
]