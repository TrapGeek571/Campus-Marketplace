import os
import sys

# Add project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_marketplace.settings')

import django
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

print("Fixing user profiles...")
for user in User.objects.all():
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        print(f"Created profile for {user.username}")
    else:
        print(f"Profile already exists for {user.username}")

print("Done! All users now have profiles.")