from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

# Create your models here.
class LostItem(models.Model):
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    ]
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books & Notes'),
        ('id_cards', 'ID Cards'),
        ('keys', 'Keys'),
        ('clothing', 'Clothing'),
        ('bags', 'Bags & Wallets'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=[('lost', 'Lost Item'), ('found', 'Found Item'), ('returned', 'Returned Item')], default='lost')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location_lost = models.CharField(max_length=200, blank=True)
    location_found = models.CharField(max_length=200, blank=True)
    date_lost = models.DateField(null=True, blank=True)
    date_found = models.DateField(null=True, blank=True)
    image = CloudinaryField(
        'image',
        folder='campus_marketplace/lostfound',
        blank=True,
        null=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'limit'},
            {'quality': 'auto:good'},
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item_type}: {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('lostfound:detail', kwargs={'pk': self.pk})

    def clean(self):
        """Model-level validation."""
        super().clean()
        today = datetime.date.today()
        
        if self.item_type == 'lost' and self.date_lost:
            if self.date_lost > today:
                raise ValidationError({'date_lost': 'Date lost cannot be in the future.'})
        
        if self.item_type == 'found' and self.date_found:
            if self.date_found > today:
                raise ValidationError({'date_found': 'Date found cannot be in the future.'})
    
    def save(self, *args, **kwargs):
        # Get old instance if exists
        old_item = None
        if self.pk:
            try:
                old_item = LostItem.objects.get(pk=self.pk)
            except LostItem.DoesNotExist:
                pass
        # Save the instance
        super().save(*args, **kwargs)
        
        # Cloudinary handles optimization automatically
        
        # Delete old Cloudinary image if changed
        if old_item and old_item.image and old_item.image != self.image:
            try:
                old_public_id = old_item.image.public_id
                if old_public_id:
                    import cloudinary.uploader
                    cloudinary.uploader.destroy(old_public_id)
            except Exception as e:
                print(f"Error deleting old Cloudinary image: {e}")

    def get_image_url(self):
        """Get optimized image URL."""
        if self.image:
            return self.image.build_url(
                width=400,
                height=300,
                crop='fill',
                quality='auto:good'
            )
        return None

    def can_edit(self, user):
        """Check if user can edit/delete this item."""
        return user == self.user or user.is_superuser

    def can_delete(self, user):
        """Check if user can delete this item."""
        return user == self.user or user.is_superuser