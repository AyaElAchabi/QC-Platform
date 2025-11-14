"""
Inference schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PredictionRequest(BaseModel):
    model_id: UUID
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    threshold: float = Field(default=0.5, ge=0, le=1)
    nms_iou_threshold: float = Field(default=0.45, ge=0, le=1)


class Detection(BaseModel):
    bbox: List[float]  # [x, y, w, h]
    class_id: UUID
    class_name: str
    score: float
    mask: Optional[List[List[float]]] = None


class PredictionResponse(BaseModel):
    run_id: UUID
    predictions: List[Detection]
    inference_time_ms: int
    preprocessing_time_ms: int
    postprocessing_time_ms: int
    device: str
    model_version: str


class BatchPredictionRequest(BaseModel):
    model_id: UUID
    image_ids: List[UUID]
    threshold: float = Field(default=0.5, ge=0, le=1)


class BatchPredictionResponse(BaseModel):
    job_id: UUID
    status: str
    total_images: int
    processed_images: int