# lostfound/urls.py
from django.urls import path
from . import views

app_name = 'lostfound'

urlpatterns = [
    # Main pages
    path('', views.lost_found_home, name='home'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('my-reports/', views.my_reports, name='my_reports'),
    
    # CRUD operations
    path('report/', views.report_item, name='report_item'),
    path('edit/<int:pk>/', views.update_item, name='update_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    
    # Status updates
    path('status/<int:pk>/<str:new_status>/', views.update_status, name='update_status'),
    
    # Quick status changes (optional shortcuts)
    path('mark-returned/<int:pk>/', views.update_status, {'new_status': 'returned'}, name='mark_returned'),
    path('mark-found/<int:pk>/', views.update_status, {'new_status': 'found'}, name='mark_found'),
    path('mark-lost/<int:pk>/', views.update_status, {'new_status': 'lost'}, name='mark_lost'),
]