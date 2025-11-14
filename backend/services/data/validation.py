"""
Image validation utilities
"""
from PIL import Image
import io
from fastapi import HTTPException

from core.config import settings


def validate_image(content: bytes, filename: str) -> tuple:
    """
    Validate image format, size, and dimensions
    
    Returns:
        (PIL.Image, width, height, format)
    
    Raises:
        HTTPException if validation fails
    """
    try:
        img = Image.open(io.BytesIO(content))
        width, height = img.size
        format_ext = img.format.lower() if img.format else "unknown"
        
        # Check format
        if format_ext not in settings.ALLOWED_IMAGE_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: Unsupported format '{format_ext}'. Allowed: {settings.ALLOWED_IMAGE_FORMATS}"
            )
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Check dimensions
        if width < 100 or height < 100:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: Dimensions too small ({width}x{height}). Minimum: 100x100"
            )
        
        return img, width, height, format_ext
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=f"{filename}: Invalid image file - {str(e)}")


def extract_exif(img: Image) -> dict:
    """
    Extract EXIF metadata from image
    
    Returns:
        Dictionary with EXIF data
    """
    exif_data = {}
    
    try:
        exif = img._getexif()
        if exif:
            from PIL.ExifTags import TAGS
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = str(value)
    except:
        pass  # No EXIF data
    
    return exif_data