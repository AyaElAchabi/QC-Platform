"""
Project, Product, Class schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from models.project import TaskType, ProjectStatus


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., max_length=100)
    description: Optional[str] = None
    product_metadata: Optional[Dict[str, Any]] = None  # ← CHANGÉ


class ProductResponse(BaseModel):
    id: UUID
    name: str
    type: str
    description: Optional[str]
    product_metadata: Optional[Dict[str, Any]]  # ← CHANGÉ
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClassCreate(BaseModel):
    product_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    color_hex: str = Field(default="#FF5733", pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None
    severity: Optional[str] = None


class ClassResponse(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    color_hex: str
    description: Optional[str]
    severity: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    product_id: Optional[UUID] = None
    task_type: TaskType
    project_metadata: Optional[Dict[str, Any]] = None  # ← CHANGÉ


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    status: Optional[ProjectStatus] = None
    project_metadata: Optional[Dict[str, Any]] = None  # ← CHANGÉ


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    owner_id: Optional[UUID]
    product_id: Optional[UUID]
    task_type: Optional[TaskType]
    status: ProjectStatus
    project_metadata: Optional[Dict[str, Any]]  # ← CHANGÉ
    created_at: datetime
    updated_at: datetime
    
    total_images: Optional[int] = None
    annotated_images: Optional[int] = None
    total_models: Optional[int] = None

    class Config:
        from_attributes = True


class ProjectMemberAdd(BaseModel):
    user_id: UUID
    role: str = Field(..., pattern="^(viewer|annotator|admin)$")