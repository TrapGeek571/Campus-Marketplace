from django.urls import path
from . import views

app_name = 'housing'

urlpatterns = [
    # Public views
    path('', views.housing_home, name='home'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('cities/', views.cities_list, name='cities'),
    path('city/<str:city>/', views.city_listings, name='city_listings'),
    
    # User views (require login)
    path('create/', views.create_listing, name='create_listing'),
    path('edit/<int:pk>/', views.update_listing, name='update_listing'),
    path('delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
]