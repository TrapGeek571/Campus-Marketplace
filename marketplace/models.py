# marketplace/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser

class CategoryManager(models.Manager):
    def create_default_categories(self):
        """Create default categories if they don't exist"""
        categories = [
            'Electronics & Gadgets',
            'Books & Textbooks',
            'Clothing & Fashion',
            'Furniture & Home',
            'Sports & Fitness',
            'Beauty & Cosmetics',
            'Jewelry & Accessories',
            'Stationery & Supplies',
            'Kitchen & Appliances',
            'ID Cards & Documents',
            'Wallets & Bags',
            'Lab Equipment',
            'Musical Instruments',
            'Art & Craft Supplies',
            'Other'
        ]
        
        for category_name in categories:
            self.get_or_create(name=category_name)
        return self.all()

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    # Add the custom manager
    objects = CategoryManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    image = CloudinaryField('product_images', blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']