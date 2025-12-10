from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

# Create your models here.
class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Brand New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', '📱 Electronics'),
        ('laptops', '💻 Laptops & Computers'),
        ('phones', '📞 Phones & Tablets'),
        ('books', '📚 Books & Textbooks'),
        ('notes', '📝 Notes & Study Material'),
        ('clothing', '👕 Clothing & Fashion'),
        ('furniture', '🛋️ Furniture'),
        ('sports', '⚽ Sports & Fitness'),
        ('accessories', '👜 Accessories'),
        ('other', '📦 Other Items'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]

    # Basic Information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    negotiable = models.BooleanField(default=False)
    fixed_price = models.BooleanField(default=False)

    # Images (up to 4 images per product)
    image1 = CloudinaryField(
        'image',
        folder='campus_marketplace/products',
        null=True,
        blank=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'fill'},
            {'quality': 'auto:good'},
        ]
    )
    image2 = CloudinaryField(
        'image',
        folder='campus_marketplace/products',
        null=True,
        blank=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'fill'},
            {'quality': 'auto:good'},
        ]
    )
    image3 = CloudinaryField(
        'image',
        folder='campus_marketplace/products',
        null=True,
        blank=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'fill'},
            {'quality': 'auto:good'},
        ]
    )
    image4 = CloudinaryField(
        'image',
        folder='campus_marketplace/products',
        null=True,
        blank=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'fill'},
            {'quality': 'auto:good'},
        ]
    )

    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_at = models.DateTimeField(null=True, blank=True)

    # Contact Information (can override user profile)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Location (campus-specific)
    location = models.CharField(max_length=200, blank=True, help_text="e.g., Main Campus, Hostel Block A, Library")
    meetup_preference = models.CharField(max_length=100, blank=True, help_text="e.g., Library, Student Center")

    # Additional Details
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    warranty_remaining = models.IntegerField(blank=True, null=True, help_text="Months remaining")
    purchase_date = models.DateField(null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Views and Engagement
    views = models.IntegerField(default=0)
    saved_by = models.ManyToManyField(User, related_name='saved_products', blank=True)

    def save(self, *args, **kwargs):
        # Get old instance if exists
        old_product = None
        if self.pk:
            try:
                old_product = Product.objects.get(pk=self.pk)
            except Product.DoesNotExist:
                pass
        
        # Save the instance
        super().save(*args, **kwargs)
        
        # Cloudinary handles optimization automatically
        
        # Optional: Delete old Cloudinary images if they were changed
        if old_product:
            image_fields = ['image1', 'image2', 'image3', 'image4']
            for field_name in image_fields:
                old_image = getattr(old_product, field_name, None)
                new_image = getattr(self, field_name, None)
                
                if old_image and old_image != new_image:
                    try:
                        old_public_id = old_image.public_id
                        if old_public_id:
                            import cloudinary.uploader
                            cloudinary.uploader.destroy(old_public_id)
                    except Exception as e:
                        print(f"Error deleting old Cloudinary image {field_name}: {e}")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.title} - ${self.price}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('marketplace:detail', kwargs={'pk': self.pk})

    def can_edit(self, user):
        """Check if user can edit this product."""
        return user == self.seller or user.is_superuser

    def can_delete(self, user):
        """Check if user can delete this product."""
        return user == self.seller or user.is_superuser

    def increment_views(self):
        """Increment view count."""
        self.views += 1
        self.save(update_fields=['views'])

    def mark_as_sold(self):
        """Mark product as sold."""
        self.status = 'sold'
        self.sold_at = timezone.now()
        self.save()

    def is_recent(self):
        """Check if product was listed in last 7 days."""
        return (timezone.now() - self.created_at).days <= 7

    def get_discount_percentage(self):
        """Calculate discount percentage if original price is provided."""
        if self.original_price and self.original_price > self.price:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return round(discount, 1)
        return None


class ProductImage(models.Model):
    """Additional images for products (optional alternative to image fields)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='marketplace/product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']


class Offer(models.Model):
    """Allow buyers to make offers on negotiable items."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('countered', 'Countered'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'buyer', 'status']

    def __str__(self):
        return f"${self.amount} offer for {self.product.title}"

    def get_image_urls(self):
        """Get optimized image URLs."""
        urls = []
        # Access images from the related product, not from the offer itself
        if self.product:
            images = [self.product.image1, self.product.image2, 
                     self.product.image3, self.product.image4]
            
            for img in images:
                if img:
                    urls.append(img.build_url(
                        width=400,
                        height=300,
                        crop='fill',
                        quality='auto:good'
                    ))
        return urls