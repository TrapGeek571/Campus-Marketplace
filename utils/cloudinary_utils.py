# utils/cloudinary_utils.py
import cloudinary.uploader
import cloudinary.api

def delete_cloudinary_resource(public_id):
    """Delete a resource from Cloudinary."""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error deleting Cloudinary resource {public_id}: {e}")
        return False

def get_resource_info(public_id):
    """Get information about a Cloudinary resource."""
    try:
        return cloudinary.api.resource(public_id)
    except:
        return None

def upload_image(file, folder, public_id=None):
    """Upload an image to Cloudinary."""
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            invalidate=True
        )
        return result
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None