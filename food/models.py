# food/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser

class Restaurant(models.Model):
    CUISINE_CHOICES = [
        ('local', 'Local'),
        ('fast_food', 'Fast Food'),
        ('continental', 'Continental'),
        ('asian', 'Asian'),
        ('italian', 'Italian'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES)
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    opening_hours = models.CharField(max_length=100)
    image = CloudinaryField('restaurant_images', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('menu_images', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
