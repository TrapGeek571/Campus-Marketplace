from django.db import models
from django.conf import settings
from marketplace.models import Product

class MpesaTransaction(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100)  # Account reference
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Daraja specific fields
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    response_code = models.CharField(max_length=10, blank=True)
    response_description = models.TextField(blank=True)
    callback_metadata = models.JSONField(null=True, blank=True)  # Store full callback response
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    TRANSACTION_TYPES = (
        ('product_purchase', 'Product Purchase'),
        ('seller_verification', 'Seller Verification'),
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='product_purchase')
    # (optional) reference to seller if type is verification
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verification_payments')

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status}"
