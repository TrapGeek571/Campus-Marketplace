# lostfound/urls.py
from django.urls import path
from . import views

app_name = 'lostfound'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    
    # User views (require login)
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:pk>/', views.update_item, name='update_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('my-items/', views.my_items, name='my_items'),
    path('mark-resolved/<int:pk>/', views.mark_resolved, name='mark_resolved'),
]