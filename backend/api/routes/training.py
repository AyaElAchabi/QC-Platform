from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from api.dependencies import get_db, get_current_user
from models.user import User
from models.project import Project
from models.image import ImageModel
from models.training_job import TrainingJob
from workers.tasks import train_yolo_model
from workers.celery_app import celery_app
from services.metrics.metrics_calculator import MetricsCalculator

router = APIRouter()


class TrainingConfig(BaseModel):
    model_name: str = "yolov8n"
    epochs: int = 100
    batch_size: int = 16
    img_size: int = 640
    learning_rate: float = 0.01
    patience: int = 50
    augmentation: bool = True


@router.post("/api/projects/{project_id}/train")
async def start_training(
    project_id: str,
    config: TrainingConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lancer l'entraînement"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Vérifier images annotées
    annotated_count = db.query(ImageModel).filter(
        ImageModel.project_id == project_id,
        ImageModel.status == "annotated"
    ).count()
    
    if annotated_count < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 annotated images. Found {annotated_count}"
        )
    
    # Créer le job
    job = TrainingJob(
        id=uuid.uuid4(),
        project_id=project_id,
        model_name=config.model_name,
        epochs=config.epochs,
        batch_size=config.batch_size,
        img_size=config.img_size,
        learning_rate=config.learning_rate,
        patience=config.patience,
        config=config.dict(),
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Lancer la tâche Celery
    try:
        print(f"🚀 Sending task to Celery for job {job.id}")
        result = train_yolo_model.delay(str(job.id))
        print(f"✅ Task sent! Task ID: {result.id}")
    except Exception as e:
        print(f"❌ Error sending task: {e}")
        import traceback
        traceback.print_exc()
    
    return {
        "job_id": str(job.id),
        "status": "pending",
        "message": f"Training started with {annotated_count} images"
    }


@router.get("/api/training/{job_id}")
async def get_training_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le statut du training"""
    
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return {
        "job_id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "current_epoch": job.current_epoch,
        "total_epochs": job.epochs,
        "metrics": job.metrics,
        "model_path": job.model_path,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }


@router.get("/api/projects/{project_id}/training-jobs")
async def list_training_jobs(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste des jobs de training"""
    
    jobs = db.query(TrainingJob).filter(
        TrainingJob.project_id == project_id
    ).order_by(TrainingJob.created_at.desc()).all()
    
    return [
        {
            "job_id": str(job.id),
            "model_name": job.model_name,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat()
        }
        for job in jobs
    ]


@router.get("/api/projects/{project_id}/training/jobs/{job_id}")
async def get_project_training_job(
    project_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir le statut d'un job de training spécifique pour un projet"""

    job = db.query(TrainingJob).filter(
        TrainingJob.id == job_id,
        TrainingJob.project_id == project_id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")

    # Gérer les métriques (peut être un array ou un objet pour les anciens jobs)
    metrics_array = []
    if job.metrics:
        if isinstance(job.metrics, list):
            # Nouveau format : déjà un array
            metrics_array = job.metrics
        elif isinstance(job.metrics, dict):
            # Ancien format : objet unique, on le convertit en array
            metrics_array = [{
                "epoch": job.current_epoch,
                **job.metrics
            }]

    # Calculer les métriques étendues si le job est terminé
    extended_metrics = None
    class_names = []

    if job.status == "completed" and metrics_array:
        # Récupérer les noms de classes du projet
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and project.classes:
            class_names = [dc.get("name", f"Class {i}") for i, dc in enumerate(project.classes)]

        # Calculer les métriques étendues
        extended_metrics = MetricsCalculator.calculate_extended_metrics(
            metrics_history=metrics_array,
            class_names=class_names if class_names else None
        )

        # Ajouter les métriques étendues au dernier élément du tableau metrics
        # pour compatibilité avec le frontend existant
        if metrics_array and extended_metrics:
            metrics_array[-1]["extended_metrics"] = extended_metrics
            metrics_array[-1]["class_names"] = class_names

    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_epoch": job.current_epoch,
        "total_epochs": job.epochs,
        "metrics": metrics_array,
        "model_path": job.model_path,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "config": job.config,
        "extended_metrics": extended_metrics,
        "class_names": class_names
    }


@router.post("/api/projects/{project_id}/training/jobs/{job_id}/cancel")
async def cancel_training_job(
    project_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Annuler un training en cours"""
    
    job = db.query(TrainingJob).filter(
        TrainingJob.id == job_id,
        TrainingJob.project_id == project_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    if job.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Tenter de révoquer la tâche Celery
    try:
        # Révoquer toutes les tâches actives pour ce job
        celery_app.control.revoke(str(job.id), terminate=True, signal='SIGKILL')
    except Exception as e:
        print(f"Warning: Could not revoke Celery task: {e}")
    
    # Mettre à jour le statut du job
    job.status = "cancelled"
    job.error_message = f"Training cancelled by user at epoch {job.current_epoch}/{job.epochs}"
    job.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    return {
        "id": str(job.id),
        "status": job.status,
        "message": "Training job cancelled successfully"
    }
