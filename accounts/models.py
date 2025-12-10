from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import cloudinary.uploader

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_pic = CloudinaryField(
        'image',
        folder='campus_marketplace/profile_pics',
        default='campus_marketplace/profile_pics/default_user',  # Cloudinary public_id
        blank=True,
        null=True,
        transformation=[
            {'width': 300, 'height': 300, 'crop': 'fill'},
            {'quality': 'auto:good'},
        ]
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Student ID")
    course = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(
        blank=True, null=True,
        choices=[(i, f'Year {i}') for i in range(1, 7)]
    )
    campus = models.CharField(max_length=100, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Verification badges
    is_verified = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    trust_score = models.IntegerField(default=50)  # Range 0-100

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_profile_pic_url(self):
        """Get profile pic URL with transformation."""
        if self.profile_pic:
            return self.profile_pic.build_url(
                width=150,
                height=150,
                crop='fill',
                gravity='face',
                quality='auto:good'
            )
        return None

    def save(self, *args, **kwargs):
        old_profile = None
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
            except Profile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Delete old Cloudinary image if changed
        if old_profile and old_profile.profile_pic:
            if old_profile.profile_pic != self.profile_pic:
                try:
                    old_public_id = old_profile.profile_pic.public_id
                    if old_public_id and 'default_user' not in old_public_id:
                        cloudinary.uploader.destroy(old_public_id)
                except Exception as e:
                    print(f"Error deleting old Cloudinary image: {e}")

# Signal to auto-create profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()