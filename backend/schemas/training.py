"""
Training and Model schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from models.project import TaskType


class TrainingConfig(BaseModel):
    epochs: int = Field(default=100, ge=1, le=1000)
    batch_size: int = Field(default=16, ge=1, le=128)
    learning_rate: float = Field(default=0.01, gt=0, le=1)
    optimizer: str = Field(default="adam", pattern="^(adam|sgd|adamw)$")
    
    pretrained: bool = True
    freeze_backbone: bool = False
    input_size: int = Field(default=640, ge=32, le=1024)
    
    augmentation: bool = True
    aug_config: Optional[Dict[str, Any]] = {
        "brightness": 0.3,
        "contrast": 0.3,
        "saturation": 0.3,
        "hue": 0.1,
        "flip_horizontal": True,
        "rotate": 15,
        "blur": True
    }
    
    early_stopping: bool = True
    patience: int = Field(default=10, ge=1, le=50)
    save_period: int = Field(default=5, ge=1, le=50)
    val_interval: int = Field(default=1, ge=1, le=50)
    
    mixed_precision: bool = True
    gradient_clip: Optional[float] = None
    warmup_epochs: int = Field(default=0, ge=0, le=10)
    label_smoothing: float = Field(default=0.0, ge=0, le=0.5)


class TrainingJobCreate(BaseModel):
    project_id: UUID
    name: Optional[str] = None
    task_type: TaskType
    model_architecture: str = Field(..., max_length=100)
    config: TrainingConfig


class TrainingJobResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: Optional[str]
    task_type: TaskType
    model_architecture: str
    config: Dict[str, Any]
    status: str
    mlflow_run_id: Optional[str]
    mlflow_experiment_id: Optional[str]
    metrics: Optional[Dict[str, Any]]
    celery_task_id: Optional[str]
    error_message: Optional[str]
    dataset_stats: Optional[Dict[str, Any]]
    progress_percent: int
    current_epoch: int
    total_epochs: Optional[int]
    started_by: Optional[UUID]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelResponse(BaseModel):
    id: UUID
    training_job_id: Optional[UUID]
    project_id: UUID
    name: str
    version: str
    task_type: TaskType
    architecture: str
    storage_path: str
    mlflow_model_uri: Optional[str]
    metrics: Dict[str, Any]
    hyperparameters: Optional[Dict[str, Any]]
    stage: str
    is_active: bool
    inference_count: int
    avg_inference_time_ms: Optional[float]
    model_card_path: Optional[str]
    created_by: Optional[UUID]
    promoted_by: Optional[UUID]
    promoted_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelPromote(BaseModel):
    stage: str = Field(..., pattern="^(staging|production|archived)$")