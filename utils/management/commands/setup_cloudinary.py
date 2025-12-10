from django.core.management.base import BaseCommand
import cloudinary.api

class Command(BaseCommand):
    help = 'Setup Cloudinary folders and upload presets'
    
    def handle(self, *args, **options):
        folders = [
            'campus_marketplace/profile_pics',
            'campus_marketplace/lostfound',
            'campus_marketplace/products',
            'campus_marketplace/housing',
            'campus_marketplace/food'
        ]
        
        for folder in folders:
            try:
                cloudinary.api.create_folder(folder)
                self.stdout.write(self.style.SUCCESS(f'Created folder: {folder}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Folder {folder}: {e}'))