# campus_marketplace/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Admin site customization - this runs after Django is ready
admin.site.site_header = "Campus Marketplace Administration"
admin.site.site_title = "Campus Marketplace Admin"
admin.site.index_title = "Welcome to Campus Marketplace Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('lostfound/', include('lostfound.urls')),
    path('housing/', include('housing.urls')),
    path('food/', include('food.urls')),
    #path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

# Add URL patterns for serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)