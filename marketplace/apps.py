# marketplace/apps.py
from django.apps import AppConfig

class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    
    def ready(self):
        # Only run this code when Django is fully loaded and ready
        # This prevents the AppRegistryNotReady error
        import sys
        
        # Skip during makemigrations/migrate commands
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return
        
        # Only import and run when Django is fully ready
        try:
            # Use django.apps to get models to avoid circular imports
            from django.apps import apps
            
            # Check if the Category model is already loaded
            Category = apps.get_model('marketplace', 'Category')
            
            # Import here to avoid circular imports
            from django.db import connection
            
            # Check if database table exists
            with connection.cursor() as cursor:
                table_names = connection.introspection.table_names()
                if 'marketplace_category' in table_names:
                    # Create default categories if none exist
                    if Category.objects.count() == 0:
                        Category.objects.create_default_categories()
                        print("✓ Default categories created for marketplace")
        except Exception as e:
            # Database might not be ready yet, that's okay
            pass