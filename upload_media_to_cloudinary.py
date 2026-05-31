import os
import sys
import django

# Setup Django environment to access settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import cloudinary
import cloudinary.uploader

# Configure Cloudinary from Django settings
cloudinary.config(
    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
    api_key = settings.CLOUDINARY_STORAGE.get('API_KEY'),
    api_secret = settings.CLOUDINARY_STORAGE.get('API_SECRET'),
    secure = True
)

media_root = settings.MEDIA_ROOT

def upload_folder(root_path, prefix=""):
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Build public_id relative to media root
            rel_path = os.path.relpath(file_path, media_root).replace('\\', '/')
            public_id = f"media/{rel_path}"  # optional folder prefix
            try:
                cloudinary.uploader.upload(file_path, public_id=public_id, overwrite=True, resource_type='auto')
                print(f"Uploaded: {public_id}")
            except Exception as e:
                print(f"Failed {public_id}: {e}")

if __name__ == "__main__":
    if not os.path.isdir(media_root):
        print(f"Media directory not found: {media_root}")
        sys.exit(1)
    upload_folder(media_root)
    print("Upload completed.")
