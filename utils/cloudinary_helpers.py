# utils/cloudinary_helpers.py
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings

def upload_to_cloudinary(file, folder='campus_marketplace', resource_type='auto'):
    """Helper function to upload files to Cloudinary."""
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            overwrite=False,
            invalidate=True
        )
        return result
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None

def delete_from_cloudinary(public_id):
    """Delete file from Cloudinary."""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error deleting from Cloudinary: {e}")
        return False

def get_cloudinary_url(public_id, transformations=None):
    """Get optimized URL from Cloudinary."""
    from cloudinary import CloudinaryImage
    
    if not public_id:
        return None
    
    if transformations is None:
        transformations = {
            'width': 800,
            'height': 600,
            'crop': 'fill',
            'quality': 'auto:good',
            'fetch_format': 'auto'
        }
    
    try:
        return CloudinaryImage(public_id).build_url(**transformations)
    except:
        # Fallback URL
        cloud_name = cloudinary.config().cloud_name
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"