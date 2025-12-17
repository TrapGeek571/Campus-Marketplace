# marketplace/apps.py
from django.apps import AppConfig

class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    
    def ready(self):
        # Import here to avoid circular imports
        try:
            from .models import Category
            # Create default categories if none exist
            if Category.objects.count() == 0:
                Category.objects.create_default_categories()
                print("Default categories created!")
        except:
            # Database might not be ready yet
            pass