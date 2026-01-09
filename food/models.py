# food/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone

class FoodVendor(models.Model):
    """Model for food vendors/restaurants"""
    
    VENDOR_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('cafe', 'Cafe'),
        ('fast_food', 'Fast Food'),
        ('food_truck', 'Food Truck'),
        ('bakery', 'Bakery'),
        ('food_stall', 'Food Stall'),
        ('other', 'Other'),
    ]
    
    CUISINE_CHOICES = [
        ('local', 'Local/Kenyan'),
        ('continental', 'Continental'),
        ('chinese', 'Chinese'),
        ('indian', 'Indian'),
        ('italian', 'Italian'),
        ('american', 'American'),
        ('arabic', 'Arabic/Middle Eastern'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('mixed', 'Mixed/International'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPE_CHOICES, default='restaurant')
    name = models.CharField(max_length=200)
    description = models.TextField()
    cuisine_type = models.CharField(max_length=50, choices=CUISINE_CHOICES, default='local')
    
    # Location
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default="Nairobi")
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    
    # Map coordinates
    latitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Longitude coordinate"
    )
    
    # Contact
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Operating hours
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    # Features
    delivery_available = models.BooleanField(default=False)
    takeaway_available = models.BooleanField(default=True)
    dine_in_available = models.BooleanField(default=True)
    accepts_card = models.BooleanField(default=False)
    wifi_available = models.BooleanField(default=False)
    
    # Images
    main_image = CloudinaryField(
        'food_vendor_images',
        folder='campus_marketplace/food',
        blank=True,
        null=True,
        help_text="Main photo of the restaurant"
    )
    image_2 = CloudinaryField('food_vendor_images', folder='campus_marketplace/food', blank=True, null=True)
    image_3 = CloudinaryField('food_vendor_images', folder='campus_marketplace/food', blank=True, null=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Food Vendor"
        verbose_name_plural = "Food Vendors"
    
    def __str__(self):
        return f"{self.name} - {self.get_cuisine_type_display()}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('food:vendor_detail', kwargs={'pk': self.pk})
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def coordinates(self):
        """Return coordinates as tuple if available"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    @property
    def operating_hours(self):
        """Format operating hours"""
        return f"{self.opening_time.strftime('%I:%M %p')} - {self.closing_time.strftime('%I:%M %p')}"


class MenuItem(models.Model):
    """Model for menu items"""
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('appetizer', 'Appetizer'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('drink', 'Drink'),
        ('snack', 'Snack'),
    ]
    
    vendor = models.ForeignKey(FoodVendor, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main_course')
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = CloudinaryField(
        'menu_item_images',
        folder='campus_marketplace/food/menu',
        blank=True,
        null=True
    )
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - KSh {self.price}"


class FoodReview(models.Model):
    """Reviews for food vendors"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    vendor = models.ForeignKey(FoodVendor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['vendor', 'user']  # One review per user per vendor
    
    def __str__(self):
        return f"{self.user.username} - {self.vendor.name} ({self.rating} stars)"