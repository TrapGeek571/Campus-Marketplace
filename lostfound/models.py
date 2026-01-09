# lostfound/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import datetime
from cloudinary.models import CloudinaryField

class LostFoundItem(models.Model):
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    ]
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books & Notes'),
        ('keys', 'Keys'),
        ('wallet', 'Wallet/Purse'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    contact_info = models.TextField(help_text="Your contact information (phone, email, etc.)")
    
    # Using simple DateField with HTML5 input
    date_lost = models.DateField(
        help_text="Date when the item was lost or found",
        validators=[
            MaxValueValidator(limit_value=timezone.now().date()),
            MinValueValidator(limit_value=timezone.now().date() - datetime.timedelta(days=365))
        ]
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    
    # CHANGED: Using CloudinaryField instead of ImageField
    image = CloudinaryField(
        'lost_found_images',
        folder='campus_marketplace/lost_found',
        blank=True,
        null=True,
        help_text="Upload an image of the item"
    )
    
    #is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lost & Found Item"
        verbose_name_plural = "Lost & Found Items"
    
    def __str__(self):
        return f"{self.item_name} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('lostfound:item_detail', kwargs={'pk': self.pk})
    
    @property
    def image_url(self):
        """Return image URL with optimized size"""
        if self.image:
            # Return optimized version (300x300 cropped)
            return self.image.build_url(width=300, height=300, crop="fill")
        return None