"""TextFile class for handling text files."""
import os

from PIL import Image, ExifTags
from filux_framework.io.File import File

class ImageFile(File):
    """A class for image file operations and data."""
    def __init__(self, path:str):
        super().__init__(path)
        self._image = None
        try:
            self._image = Image.open(self._path)
        except Exception as e:
            print(f"Failed to open image: {e}")

    @property
    def dimensions(self):
        """Return (width, height) of the image."""
        if self._image:
            return self._image.size
        return None

    @property
    def image_format(self):
        """Return the format of the image (e.g., JPEG, PNG)."""
        if self._image:
            return self._image.format
        return None

    @property
    def is_corrupted(self):
        """Check if the image file is corrupted."""
        try:
            if self._image:
                self._image.verify()
                return False
        except Exception:
            return True
        return True

    @property
    def exif(self):
        """Return raw EXIF data as a dictionary (if present)."""
        if self._image and hasattr(self._image, 'getexif'):
            try:
                exif_raw = self._image.getexif()
                if exif_raw:
                    return {
                        ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()
                    }
            except Exception as e:
                print(f"Error reading EXIF: {e}")
        return {}

    def generate_thumbnail(self, max_size=(128, 128), save_to=None):
        """Generate a thumbnail."""
        if self._image:
            thumb = self._image.copy()
            thumb.thumbnail(max_size)
            if save_to:
                thumb.save(save_to)
            return thumb
        return None

    def convert(self, format, save_to=None):
        """Convert image to a different format."""
        if self._image:
            target = save_to or (os.path.splitext(self._path)[0] + '.' + format.lower())
            self._image.convert('RGB').save(target, format=format.upper())
            return target
        return None