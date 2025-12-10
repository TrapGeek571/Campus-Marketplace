from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
import hashlib
import time
import os

@deconstructible
class CloudinaryStorage(Storage):
    """
    Custom Cloudinary Storage for Django.
    Provides more control than the default cloudinary_storage.
    """
    
    def __init__(self, folder=None, resource_type='image', **kwargs):
        self.folder = folder or 'campus_marketplace'
        self.resource_type = resource_type
        self.cloudinary_config = kwargs
    
    def _open(self, name, mode='rb'):
        """
        Open file from Cloudinary. Cloudinary doesn't support opening
        files in the traditional sense, so we return None.
        """
        return None
    
    def _save(self, name, content):
        """
        Save file to Cloudinary.
        
        Args:
            name: Filename
            content: File content (InMemoryUploadedFile)
        
        Returns:
            public_id: Cloudinary public ID
        """
        # Generate unique public_id
        timestamp = str(int(time.time()))
        file_hash = hashlib.md5(content.read()).hexdigest()[:8]
        content.seek(0)  # Reset pointer
        
        # Extract filename without extension
        filename = os.path.splitext(name)[0]
        extension = os.path.splitext(name)[1]
        
        # Create public_id
        public_id = f"{self.folder}/{filename}_{file_hash}_{timestamp}"
        
        # Upload options
        upload_options = {
            'public_id': public_id,
            'resource_type': self.resource_type,
            'folder': self.folder,
            'overwrite': False,  # Don't overwrite existing
            'invalidate': True,  # Invalidate CDN cache
            'quality': 'auto:good',
            'fetch_format': 'auto',
            **self.cloudinary_config
        }
        
        # Upload to Cloudinary
        try:
            result = cloudinary.uploader.upload(
                content,
                **upload_options
            )
            return result['public_id']
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            raise
    
    def delete(self, name):
        """
        Delete file from Cloudinary.
        
        Args:
            name: Cloudinary public_id
        """
        try:
            result = cloudinary.uploader.destroy(name)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
            return False
    
    def exists(self, name):
        """
        Check if file exists in Cloudinary.
        
        Args:
            name: Cloudinary public_id
        """
        try:
            cloudinary.api.resource(name)
            return True
        except cloudinary.api.Error as e:
            if e.http_code == 404:
                return False
            raise
    
    def url(self, name):
        """
        Get Cloudinary URL for file.
        
        Args:
            name: Cloudinary public_id
        """
        if not name:
            return ''
        
        # If it's already a URL, return as-is
        if name.startswith('http'):
            return name
        
        # Build Cloudinary URL with optimizations
        from cloudinary import CloudinaryImage
        try:
            return CloudinaryImage(name).build_url(
                secure=True,
                quality='auto:good',
                fetch_format='auto'
            )
        except:
            return f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/image/upload/{name}"
    
    def size(self, name):
        """
        Get file size from Cloudinary.
        
        Args:
            name: Cloudinary public_id
        """
        try:
            resource = cloudinary.api.resource(name)
            return resource.get('bytes', 0)
        except:
            return 0
    
    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's free on the target storage system.
        Cloudinary handles unique names with public_id.
        """
        return name
    
    def generate_filename(self, filename):
        """
        Validate the filename and return a filename to be passed to save().
        """
        return filename

@deconstructible
class CloudinaryImageStorage(CloudinaryStorage):
    """Storage for images with image-specific optimizations."""
    
    def __init__(self, folder='campus_marketplace/images', **kwargs):
        super().__init__(folder=folder, resource_type='image', **kwargs)
    
    def _save(self, name, content):
        # Add image-specific transformations
        self.cloudinary_config.update({
            'transformation': [
                {'width': 1200, 'height': 1200, 'crop': 'limit'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'},
            ]
        })
        return super()._save(name, content)

@deconstructible
class CloudinaryDocumentStorage(CloudinaryStorage):
    """Storage for documents (PDF, DOC, etc.)."""
    
    def __init__(self, folder='campus_marketplace/documents', **kwargs):
        super().__init__(folder=folder, resource_type='raw', **kwargs)

@deconstructible  
class CloudinaryVideoStorage(CloudinaryStorage):
    """Storage for videos."""
    
    def __init__(self, folder='campus_marketplace/videos', **kwargs):
        super().__init__(folder=folder, resource_type='video', **kwargs)
    
    def _save(self, name, content):
        # Add video-specific optimizations
        self.cloudinary_config.update({
            'resource_type': 'video',
            'transformation': [
                {'quality': 'auto:good'},
            ]
        })
        return super()._save(name, content)