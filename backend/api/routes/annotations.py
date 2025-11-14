"""
Routes pour la gestion des annotations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid
from datetime import datetime

from api.dependencies import get_db, get_current_user
from models.user import User
from models.annotation import Annotation
from models.image import ImageModel

router = APIRouter()


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class AnnotationCreate(BaseModel):
    class_name: str
    bbox: BoundingBox


class AnnotationBatch(BaseModel):
    annotations: List[AnnotationCreate]


@router.post("/api/images/{image_id}/annotations")
async def save_annotations(
    image_id: str,
    data: AnnotationBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    db.query(Annotation).filter(Annotation.image_id == image_id).delete()
    
    saved_annotations = []
    for ann in data.annotations:
        annotation = Annotation(
            id=str(uuid.uuid4()),
            image_id=image_id,
            class_name=ann.class_name,
            bbox=ann.bbox.dict(),
            confidence=1.0,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
        )
        db.add(annotation)
        saved_annotations.append(annotation)
    
    image.status = "annotated"
    db.commit()
    
    return {
        "message": f"{len(saved_annotations)} annotations saved",
        "count": len(saved_annotations)
    }


@router.get("/api/images/{image_id}/annotations")
async def get_annotations(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    annotations = db.query(Annotation).filter(
        Annotation.image_id == image_id
    ).all()
    
    return [
        {
            "id": ann.id,
            "class_name": ann.class_name,
            "bbox": ann.bbox,
            "confidence": ann.confidence,
            "created_at": ann.created_at.isoformat(),
        }
        for ann in annotations
    ]
