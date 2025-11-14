"""
Data management routes (upload, list, delete)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import hashlib
from PIL import Image as PILImage
import io

from schemas.images import ImageUploadResponse, ImageResponse
from api.dependencies import get_db, get_current_user, require_role
from services.data.validation import validate_image, extract_exif
from services.data.storage import StorageService
from services.data.thumbnail import generate_thumbnail
from models.image import Image
from models.user import User, UserRole
from core.config import settings

router = APIRouter(prefix="/data", tags=["Data Management"])


@router.post("/upload", response_model=List[ImageUploadResponse])
async def upload_images(
    project_id: UUID = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.OPERATOR, UserRole.ADMIN]))
):
    """
    Upload images to a project
    
    Process:
    1. Validate format, size, dimensions
    2. Calculate MD5 hash (deduplication)
    3. Extract EXIF metadata
    4. Store in MinIO
    5. Generate thumbnail
    6. Save metadata to PostgreSQL
    """
    uploaded_images = []
    
    for file in files:
        # Read file content
        content = await file.read()
        
        # Validate image
        img, width, height, format_ext = validate_image(content, file.filename)
        
        # Calculate hash
        file_hash = hashlib.md5(content).hexdigest()
        
        # Check for duplicates
        existing = db.query(Image).filter(Image.file_hash == file_hash).first()
        if existing:
            uploaded_images.append(existing)
            continue
        
        # Extract EXIF
        exif_data = extract_exif(img)
        
        # Upload to MinIO
        storage_path = StorageService.upload_image(
            project_id=str(project_id),
            file_hash=file_hash,
            content=content,
            format=format_ext
        )
        
        # Generate and upload thumbnail
        thumb_bytes = generate_thumbnail(img, size=(200, 200))
        thumbnail_path = StorageService.upload_thumbnail(
            project_id=str(project_id),
            file_hash=file_hash,
            content=thumb_bytes
        )
        
        # Save to DB
        new_image = Image(
            project_id=project_id,
            filename=file.filename,
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            file_hash=file_hash,
            width=width,
            height=height,
            file_size_bytes=len(content),
            format=format_ext.upper(),
            exif_metadata=exif_data,
            uploaded_by=current_user.id
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        
        uploaded_images.append(new_image)
    
    return uploaded_images


@router.get("/images", response_model=List[ImageResponse])
async def list_images(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    split: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List images with pagination and filters
    """
    query = db.query(Image)
    
    if project_id:
        query = query.filter(Image.project_id == project_id)
    if status:
        query = query.filter(Image.status == status)
    if split:
        query = query.filter(Image.split == split)
    
    # Pagination
    offset = (page - 1) * page_size
    images = query.order_by(Image.created_at.desc()).offset(offset).limit(page_size).all()
    
    return images


@router.get("/image/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get image metadata by ID
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image


@router.get("/thumbnail/{image_id}")
async def get_thumbnail(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get image thumbnail (streaming response)
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image or not image.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    # Stream from MinIO
    try:
        data = StorageService.get_image(image.thumbnail_path)
        return StreamingResponse(io.BytesIO(data), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{image_id}/url")
async def get_image_url(
    image_id: UUID,
    expires: int = 3600,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get presigned URL for image (temporary access)
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    url = StorageService.get_presigned_url(image.storage_path, expires_seconds=expires)
    return {"url": url, "expires_in": expires}


@router.delete("/image/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete image (soft or hard)
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if hard_delete:
        # Remove from MinIO
        try:
            StorageService.delete_image(image.storage_path)
            if image.thumbnail_path:
                StorageService.delete_image(image.thumbnail_path)
        except Exception as e:
            pass  # Log error but continue
        
        # Remove from DB
        db.delete(image)
        db.commit()
    else:
        # Soft delete
        from models.image import ImageStatus
        image.status = ImageStatus.REJECTED
        db.commit()
    
    return None