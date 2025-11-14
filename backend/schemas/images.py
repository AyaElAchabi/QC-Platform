"""
Image and Annotation schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from models.image import ImageStatus, SplitType, AnnotationSource


class BBox(BaseModel):
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)
    w: float = Field(..., ge=0, le=1)
    h: float = Field(..., ge=0, le=1)


class SegmentationMask(BaseModel):
    segmentation: List[List[float]]
    area: float


class ImageUploadResponse(BaseModel):
    id: UUID
    filename: str
    storage_path: str
    thumbnail_path: Optional[str]
    file_hash: str
    width: int
    height: int
    file_size_bytes: int
    format: str
    status: ImageStatus
    created_at: datetime


class ImageResponse(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    storage_path: str
    thumbnail_path: Optional[str]
    file_hash: str
    width: int
    height: int
    file_size_bytes: Optional[int]
    format: Optional[str]
    exif_metadata: Optional[Dict[str, Any]]
    status: ImageStatus
    split: Optional[SplitType]
    annotation_count: int
    uploaded_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnotationCreate(BaseModel):
    image_id: UUID
    class_id: UUID
    bbox: BBox
    mask: Optional[SegmentationMask] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    source: AnnotationSource = AnnotationSource.MANUAL


class AnnotationUpdate(BaseModel):
    bbox: Optional[BBox] = None
    mask: Optional[SegmentationMask] = None
    class_id: Optional[UUID] = None
    is_verified: Optional[bool] = None


class AnnotationResponse(BaseModel):
    id: UUID
    image_id: UUID
    class_id: UUID
    bbox: Dict[str, float]
    mask: Optional[Dict[str, Any]]
    confidence: Optional[float]
    source: AnnotationSource
    is_verified: bool
    created_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetExportRequest(BaseModel):
    project_id: UUID
    format: str = Field(..., pattern="^(coco|yolo|pascal_voc)$")
    split_ratios: Optional[Dict[str, float]] = {"train": 0.7, "val": 0.2, "test": 0.1}