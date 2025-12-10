# fix_debug.py - FIXED VERSION
import os
import re

print("🔧 Fixing Django DEBUG and ALLOWED_HOSTS settings...")

# Find settings.py file
project_root = r"C:\Users\w\OneDrive\Desktop\websitedevelpt2025\campus_marketplace"
settings_path = os.path.join(project_root, "campus_marketplace", "settings.py")

print(f"Looking for settings.py at: {settings_path}")

if not os.path.exists(settings_path):
    print("❌ settings.py not found at expected location. Searching...")
    # Try to find it
    for root, dirs, files in os.walk(project_root):
        if "settings.py" in files:
            settings_path = os.path.join(root, "settings.py")
            print(f"✅ Found settings.py at: {settings_path}")
            break

# Read the file in BINARY mode to avoid encoding issues
try:
    with open(settings_path, 'rb') as f:
        content_bytes = f.read()
    
    # Decode with error handling
    try:
        content = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        content = content_bytes.decode('utf-8', errors='ignore')
    
    print(f"📄 Read settings.py successfully ({len(content)} characters)")
    
    # Count changes
    changes_made = 0
    
    # Replace DEBUG = False with DEBUG = True
    if 'DEBUG = False' in content:
        content = content.replace('DEBUG = False', 'DEBUG = True')
        changes_made += 1
        print("✅ Changed DEBUG = False → DEBUG = True")
    elif 'DEBUG=False' in content:
        content = content.replace('DEBUG=False', 'DEBUG=True')
        changes_made += 1
        print("✅ Changed DEBUG=False → DEBUG=True")
    
    # Replace ALLOWED_HOSTS = [] with proper hosts
    if 'ALLOWED_HOSTS = []' in content:
        content = content.replace('ALLOWED_HOSTS = []', "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.*']")
        changes_made += 1
        print("✅ Changed ALLOWED_HOSTS = [] → ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.*']")
    
    # Also fix if ALLOWED_HOSTS is empty list
    if "ALLOWED_HOSTS = []" in content:
        content = content.replace("ALLOWED_HOSTS = []", "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.*']")
        changes_made += 1
        print("✅ Fixed empty ALLOWED_HOSTS list")
    
    # Fix DEBUG from config()
    content = re.sub(r"DEBUG\s*=\s*config\([^)]*False[^)]*\)", "DEBUG = True", content)
    if changes_made == 0 and 'DEBUG = config' in content:
        print("✅ Fixed DEBUG from config()")
        changes_made += 1
    
    # Write back in UTF-8
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎯 Total changes made: {changes_made}")
    print("✅ Successfully fixed settings.py!")
    print("\nNow run: python manage.py runserver")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nLet's try an alternative approach...")
    
    # Alternative: Create a fresh settings file
    create_fresh_settings = input("Create fresh settings.py? (y/n): ")
    if create_fresh_settings.lower() == 'y':
        create_fresh_settings_file(project_root)

def create_fresh_settings_file(project_root):
    """Create a fresh settings.py file."""
    settings_path = os.path.join(project_root, "campus_marketplace", "settings.py")
    
    # Backup old file
    backup_path = settings_path + '.backup'
    if os.path.exists(settings_path):
        os.rename(settings_path, backup_path)
        print(f"📦 Backed up old settings to: {backup_path}")
    
    # Create new settings
    fresh_settings = """
"""
Django settings for campus_marketplace project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production!
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-dev-secret-key-12345-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # ← DEVELOPMENT MODE

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'accounts',
    'marketplace',
    'lostfound',
    'housing',
    'food',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campus_marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'campus_marketplace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/ref/settings/#internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cloudinary Configuration
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary (add your credentials here)
cloudinary.config(
    cloud_name='your-cloud-name',      # ← Replace with your Cloudinary cloud name
    api_key='your-api-key',           # ← Replace with your Cloudinary API key
    api_secret='your-api-secret',     # ← Replace with your Cloudinary API secret
    secure=True
)

# Cloudinary storage for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
"""
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(fresh_settings)
    
    print(f"✅ Created fresh settings.py at: {settings_path}")
    print("⚠️  Don't forget to add your Cloudinary credentials!")