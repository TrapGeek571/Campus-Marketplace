from django.core.management.base import BaseCommand
from django.utils import timezone
from marketplace.models import Product

class Command(BaseCommand):
    help = 'Mark products as expired if past expiry date'

    def handle(self, *args, **options):
        expired_products = Product.objects.filter(
            expires_at__lte=timezone.now(),
            expired=False,
            is_sold=False
        )
        count = expired_products.update(expired=True)
        self.stdout.write(f"{count} products marked as expired.")