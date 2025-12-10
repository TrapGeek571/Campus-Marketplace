from django.urls import path
from . import views

app_name = 'lostfound'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/returned/', views.mark_returned, name='mark_returned'),
    path('admin/manage/', views.admin_manage, name='admin_manage'),
]
