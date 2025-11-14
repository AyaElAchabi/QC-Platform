from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import hashlib
import uuid
import os
from datetime import datetime
from PIL import Image as PILImage
import io
from minio import Minio
from fastapi.responses import StreamingResponse, FileResponse

from api.dependencies import get_db, get_current_user
from models.user import User
from models.image import ImageModel
from models.annotation import Annotation

router = APIRouter()

minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
BUCKET_NAME = "mlops-images"

try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except Exception as e:
    print(f"MinIO setup: {e}")


@router.get("/api/projects/{project_id}/images")
async def get_project_images(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get images - LIMITED TO 100"""
    images = db.query(ImageModel).filter(ImageModel.project_id == project_id).limit(100).all()
    
    result = []
    for img in images:
        annotation_count = db.query(func.count(Annotation.id)).filter(Annotation.image_id == img.id).scalar() or 0
        result.append({
            "id": img.id,
            "project_id": img.project_id,
            "filename": img.filename,
            "width": img.width,
            "height": img.height,
            "status": img.status,
            "annotation_count": annotation_count,
            "created_at": img.created_at.isoformat(),
        })
    return result


@router.get("/api/images/{image_id}/file")
async def get_image_file(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        if image.storage_path.startswith("/app/storage/"):
            if os.path.exists(image.storage_path):
                return FileResponse(image.storage_path, media_type="image/jpeg")
            else:
                raise HTTPException(status_code=404, detail="Not found")
        else:
            response = minio_client.get_object(BUCKET_NAME, image.storage_path)
            file_data = response.read()
            response.close()
            response.release_conn()
            return StreamingResponse(io.BytesIO(file_data), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/projects/{project_id}/images/upload")
async def upload_images(project_id: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    uploaded_images = []
    for file in files:
        try:
            contents = await file.read()
            file_hash = hashlib.md5(contents).hexdigest()
            existing = db.query(ImageModel).filter(ImageModel.file_hash == file_hash, ImageModel.project_id == project_id).first()
            if existing:
                continue
            img = PILImage.open(io.BytesIO(contents))
            width, height = img.size
            image_id = str(uuid.uuid4())
            storage_path = f"projects/{project_id}/images/{image_id}_{file.filename}"
            minio_client.put_object(BUCKET_NAME, storage_path, io.BytesIO(contents), length=len(contents), content_type=file.content_type or "image/jpeg")
            new_image = ImageModel(id=image_id, project_id=project_id, filename=file.filename, storage_path=storage_path, file_hash=file_hash, width=width, height=height, status="uploaded", created_at=datetime.utcnow())
            db.add(new_image)
            uploaded_images.append(new_image)
        except:
            continue
    db.commit()
    return {"message": f"{len(uploaded_images)} uploaded", "images": [{"id": i.id, "filename": i.filename} for i in uploaded_images]}


@router.delete("/api/images/{image_id}")
async def delete_image(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        if image.storage_path.startswith("/app/storage/"):
            if os.path.exists(image.storage_path):
                os.remove(image.storage_path)
        else:
            minio_client.remove_object(BUCKET_NAME, image.storage_path)
    except:
        pass
    db.delete(image)
    db.commit()
    return {"message": "Deleted"}
