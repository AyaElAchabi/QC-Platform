"""
Models API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os

from api.dependencies import get_db, get_current_user
from models.model import Model
from models.user import User
from core.minio_client import minio_client

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=List[dict])
async def list_models(
    project_id: str = None,
    stage: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all models, optionally filtered by project_id or stage
    """
    query = db.query(Model)
    
    if project_id:
        query = query.filter(Model.project_id == project_id)
    
    if stage:
        query = query.filter(Model.stage == stage)
    
    models = query.order_by(Model.created_at.desc()).all()
    
    return [
        {
            "id": str(model.id),
            "name": model.name,
            "version": model.version,
            "architecture": model.architecture,
            "task_type": model.task_type,
            "stage": model.stage,
            "is_active": model.is_active,
            "project_id": str(model.project_id),
            "training_job_id": str(model.training_job_id) if model.training_job_id else None,
            "storage_path": model.storage_path,
            "metrics": model.metrics,
            "hyperparameters": model.hyperparameters,
            "inference_count": model.inference_count or 0,
            "avg_inference_time_ms": model.avg_inference_time_ms,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }
        for model in models
    ]


@router.get("/{model_id}")
async def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific model by ID
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "id": str(model.id),
        "name": model.name,
        "version": model.version,
        "architecture": model.architecture,
        "task_type": model.task_type,
        "stage": model.stage,
        "is_active": model.is_active,
        "project_id": str(model.project_id),
        "training_job_id": str(model.training_job_id) if model.training_job_id else None,
        "storage_path": model.storage_path,
        "mlflow_model_uri": model.mlflow_model_uri,
        "metrics": model.metrics,
        "hyperparameters": model.hyperparameters,
        "inference_count": model.inference_count or 0,
        "avg_inference_time_ms": model.avg_inference_time_ms,
        "model_card_path": model.model_card_path,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        "promoted_at": model.promoted_at.isoformat() if model.promoted_at else None,
    }


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a model
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(model)
    db.commit()
    
    return {"message": "Model deleted successfully"}


@router.get("/{model_id}/download")
async def download_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific model by ID
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Get the model file from MinIO
    try:
        # Extract filename from storage path
        filename = model.storage_path.split("/")[-1]
        temp_file_path = f"/tmp/{filename}"
        
        # Download from MinIO
        minio_client.client.fget_object(
            bucket_name="mlops-models",
            object_name=model.storage_path,
            file_path=temp_file_path
        )
        
        # Stream the file to user
        def iterfile():
            with open(temp_file_path, mode="rb") as file_like:
                yield from file_like
            # Cleanup temp file after streaming
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        return StreamingResponse(
            iterfile(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading model: {str(e)}")
