# food/urls.py
from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    path('', views.home, name='home'),
    path('vendors/', views.FoodVendorListView.as_view(), name='vendor_list'),
    path('vendor/<int:pk>/', views.FoodVendorDetailView.as_view(), name='vendor_detail'),
    path('vendor/add/', views.FoodVendorCreateView.as_view(), name='add_vendor'),
    path('vendor/<int:pk>/edit/', views.FoodVendorUpdateView.as_view(), name='edit_vendor'),
    path('vendor/<int:pk>/delete/', views.FoodVendorDeleteView.as_view(), name='delete_vendor'),
    path('my-restaurants/', views.MyRestaurantsView.as_view(), name='my_restaurants'),
    path('vendor/<int:vendor_pk>/review/add/', views.add_review, name='add_review'),
    path('vendor/<int:vendor_pk>/menu/add/', views.MenuItemCreateView.as_view(), name='add_menu_item'),
    path('menu/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='edit_menu_item'),
    path('menu/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='delete_menu_item'),
    path('vendor/<int:pk>/menu/manage/', views.RestaurantMenuManagementView.as_view(), name='manage_menu'),
]