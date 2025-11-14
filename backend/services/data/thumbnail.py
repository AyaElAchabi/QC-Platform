"""
Thumbnail generation
"""
from PIL import Image
import io


def generate_thumbnail(img: Image, size: tuple = (200, 200)) -> bytes:
    """
    Generate thumbnail from PIL Image
    
    Args:
        img: PIL Image object
        size: Thumbnail size (width, height)
    
    Returns:
        JPEG bytes
    """
    img_copy = img.copy()
    img_copy.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary (for PNG with alpha)
    if img_copy.mode in ("RGBA", "P"):
        rgb_img = Image.new("RGB", img_copy.size, (255, 255, 255))
        rgb_img.paste(img_copy, mask=img_copy.split()[3] if img_copy.mode == "RGBA" else None)
        img_copy = rgb_img
    
    # Save to bytes
    buffer = io.BytesIO()
    img_copy.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()