from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone
from decimal import Decimal

class HousingListing(models.Model):
    LISTING_TYPE_CHOICES = [
        ('rental', 'Rental'),
        ('sublet', 'Sublet'),
        ('roommate', 'Roommate Wanted'),
        ('housing_wanted', 'Housing Wanted'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('dorm', 'Dorm Room'),
        ('other', 'Other'),
    ]
    
    FURNISHED_CHOICES = [
        ('furnished', 'Fully Furnished'),
        ('semi', 'Semi-Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='rental')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=200, default="P.O. Box 43844-00100, Nairobi")
    city = models.CharField(max_length=100, default="Nairobi")
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=12, 
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Latitude coordinate (optional)"
    )
    longitude = models.DecimalField(
        max_digits=12, 
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Longitude coordinate (optional)"
    )
    def save(self, *args, **kwargs):
        """Override save to automatically geocode address if coordinates are missing"""
        if (self.address and self.city) and (not self.latitude or not self.longitude):
            # We'll implement geocoding later
            pass
        super().save(*args, **kwargs)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_period = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
        ('semester', 'Per Semester'),
    ], default='monthly')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    utilities_included = models.BooleanField(default=False)
    
    # Property details
    bedrooms = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0.5)])  # 1.5, 2.5 etc
    square_meters = models.PositiveIntegerField(blank=True, null=True)
    furnished = models.CharField(max_length=20, choices=FURNISHED_CHOICES, default='unfurnished')
    available_from = models.DateField()
    lease_duration = models.CharField(max_length=50, blank=True, null=True)
    
    # Amenities (store as comma-separated)
    amenities = models.TextField(blank=True, null=True, help_text="Comma-separated list of amenities")
    
    # Contact
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True, null=True)
    contact_preference = models.CharField(max_length=20, choices=[
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('both', 'Both'),
    ], default='both')
    
    # Images
    main_image = CloudinaryField(
        'housing_images',
        folder='campus_marketplace/housing',
        blank=True,
        null=True,
        help_text="Main photo of the property"
    )
    image_2 = CloudinaryField('housing_images', folder='campus_marketplace/housing', blank=True, null=True)
    image_3 = CloudinaryField('housing_images', folder='campus_marketplace/housing', blank=True, null=True)
    image_4 = CloudinaryField('housing_images', folder='campus_marketplace/housing', blank=True, null=True)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Housing Listing"
        verbose_name_plural = "Housing Listings"
    
    def __str__(self):
        return f"{self.title} - {self.get_listing_type_display()}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('housing:listing_detail', kwargs={'pk': self.pk})
    
    def get_amenities_list(self):
        """Return amenities as list"""
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def price_display(self):
        """Formatted price display"""
        period_map = {
            'monthly': '/month',
            'weekly': '/week',
            'daily': '/day',
            'semester': '/semester'
        }
        return f"KSh {self.price:,.0f}{period_map.get(self.price_period, '')}"
    
    def coordinates(self):
        """Return coordinates as tuple if available"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
class FavoriteListing(models.Model):
    """For users to save favorite listings"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(HousingListing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'listing']
        verbose_name = "Favorite Listing"
        verbose_name_plural = "Favorite Listings"
    
    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"