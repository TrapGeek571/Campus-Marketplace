# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

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