# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

class SellerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    is_verified = models.BooleanField(default=False)
    verified_until = models.DateTimeField(null=True, blank=True)
    max_listings = models.IntegerField(default=1)  # Base limit for unverified
    listing_duration_days = models.IntegerField(default=7)  # Base duration for unverified
    store_name = models.CharField(max_length=100, blank=True)
    store_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Verified: {self.is_verified}"

    def can_post_more_listings(self):
        """Check if seller can post a new product based on their current active listings count."""
        # Import Product here to avoid circular import
        from marketplace.models import Product
        active_count = Product.objects.filter(seller=self.user, is_sold=False, expired=False).count()
        return active_count < self.max_listings

    def get_listing_expiry_date(self):
        """Return the expiry date for a new listing based on seller's duration."""
        return timezone.now() + timedelta(days=self.listing_duration_days)

    def activate_verified(self, duration_days=30):
        """Activate verified status for given number of days."""
        self.is_verified = True
        self.verified_until = timezone.now() + timedelta(days=duration_days)
        self.max_listings = 10  # or any number you prefer
        self.listing_duration_days = 30
        self.save()

    def check_verification_expiry(self):
        """Call this periodically to expire verification."""
        if self.is_verified and self.verified_until and self.verified_until < timezone.now():
            self.is_verified = False
            self.max_listings = 1
            self.listing_duration_days = 7
            self.save()
            
@receiver(post_save, sender='accounts.CustomUser')
def create_seller_profile(sender, instance, created, **kwargs):
    if created:
        SellerProfile.objects.create(user=instance)            


# Signal to create SellerProfile for new users
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_seller_profile(sender, instance, created, **kwargs):
    if created:
        SellerProfile.objects.create(user=instance)

class Report(models.Model):
    REPORT_TYPES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('scam', 'Scam/Fraud'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    reporter = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='reports_against')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    
    # Content reference (generic foreign key would be better, but for simplicity):
    content_type = models.CharField(max_length=50, blank=True)  # e.g., 'product', 'lostfounditem', etc.
    content_id = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Report #{self.id} - {self.get_report_type_display()} by {self.reporter.username}"

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('vendor', 'Vendor'),
        ('staff', 'Staff'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField('profile_pictures', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True, null=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return full name if available, otherwise username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username