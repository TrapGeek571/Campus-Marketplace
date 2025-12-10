from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/save/', views.toggle_save, name='toggle_save'),
    path('<int:pk>/offer/', views.make_offer, name='make_offer'),
    path('<int:pk>/sold/', views.mark_as_sold, name='mark_as_sold'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('saved/', views.saved_items, name='saved_items'),
    path('category/<str:category>/', views.category_view, name='category'),
]







