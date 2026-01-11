from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from api.dependencies import get_db, get_current_user
from models.user import User
from models.project import Project
from models.image import ImageModel
from models.model import Model

router = APIRouter()

class DefectClass(BaseModel):
    name: str
    color: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: str = "detection"
    classes: List[DefectClass] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    classes: Optional[List[DefectClass]] = None

@router.get("/api/projects")
async def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = db.query(Project).all()
    result = []
    for p in projects:
        total = db.query(func.count(ImageModel.id)).filter(ImageModel.project_id == p.id).scalar() or 0
        annotated = db.query(func.count(ImageModel.id)).filter(ImageModel.project_id == p.id, ImageModel.status == "annotated").scalar() or 0
        models_count = db.query(func.count(Model.id)).filter(Model.project_id == p.id).scalar() or 0
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "task_type": p.task_type,
            "status": p.status,
            "classes": p.classes or [],
            "total_images": total,
            "annotated_images": annotated,
            "models_count": models_count,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat() if p.updated_at else p.created_at.isoformat(),
        })
    return result

@router.get("/api/projects/{project_id}")
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    total = db.query(func.count(ImageModel.id)).filter(ImageModel.project_id == project_id).scalar() or 0
    annotated = db.query(func.count(ImageModel.id)).filter(ImageModel.project_id == project_id, ImageModel.status == "annotated").scalar() or 0
    models_count = db.query(func.count(Model.id)).filter(Model.project_id == project_id).scalar() or 0
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "task_type": project.task_type,
        "status": project.status,
        "classes": project.classes or [],
        "total_images": total,
        "annotated_images": annotated,
        "models_count": models_count,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat() if project.updated_at else project.created_at.isoformat(),
    }

@router.post("/api/projects", status_code=201)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    classes_json = [{"name": c.name, "color": c.color} for c in project.classes]
    
    new_project = Project(
        id=str(uuid.uuid4()),
        name=project.name,
        description=project.description,
        task_type=project.task_type,
        classes=classes_json,
        owner_id=current_user.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description,
        "task_type": new_project.task_type,
        "classes": new_project.classes,
        "status": new_project.status,
        "created_at": new_project.created_at.isoformat(),
    }

@router.patch("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_update.name:
        project.name = project_update.name
    if project_update.description:
        project.description = project_update.description
    if project_update.classes:
        project.classes = [{"name": c.name, "color": c.color} for c in project_update.classes]
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "task_type": project.task_type,
        "classes": project.classes,
        "status": project.status,
        "updated_at": project.updated_at.isoformat(),
    }

@router.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
