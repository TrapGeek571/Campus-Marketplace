# lostfound/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import datetime

class LostFoundItem(models.Model):
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    ]
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('keys', 'Keys'),
        ('wallet', 'Wallet/Purse'),
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date_lost = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    image = CloudinaryField('lost_found_images', blank=True, null=True)
    contact_info = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']