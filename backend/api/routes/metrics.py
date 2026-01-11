"""
Metrics API routes
Provides endpoints for computing and retrieving model metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from api.dependencies import get_db, get_current_user
from models.user import User
from models.model import Model
from models.training_job import TrainingJob
from services.metrics import metrics_service


router = APIRouter(prefix="/api/metrics", tags=["metrics"])


# ==================== Request/Response Schemas ====================

class DetectionInput(BaseModel):
    """Format d'entrée pour une détection"""
    bbox: List[float]  # [x1, y1, x2, y2]
    class_name: str
    confidence: Optional[float] = 1.0


class GroundTruthInput(BaseModel):
    """Format d'entrée pour une ground truth"""
    bbox: List[float]  # [x1, y1, x2, y2]
    class_name: str


class ComputeMetricsRequest(BaseModel):
    """Requête pour calculer les métriques"""
    predictions: List[DetectionInput]
    ground_truths: List[GroundTruthInput]
    class_names: List[str]
    iou_threshold: float = 0.5


class MetricsResponse(BaseModel):
    """Réponse avec les métriques calculées"""
    confusion_matrix: dict
    business_metrics: dict
    auroc: float
    calibration: dict
    iou_distribution: dict
    summary: dict


# ==================== Endpoints ====================

@router.post("/compute", response_model=MetricsResponse)
async def compute_metrics(
    request: ComputeMetricsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculer les métriques complètes à partir des prédictions et ground truths.
    
    Retourne:
    - Matrice de confusion (TP, FP, FN par classe)
    - Métriques métier (precision, recall, F1)
    - AUROC
    - Calibration (ECE, courbe de fiabilité)
    - Distribution IoU
    """
    try:
        # Convertir en format dict
        predictions = [p.model_dump() for p in request.predictions]
        ground_truths = [g.model_dump() for g in request.ground_truths]
        
        # Calculer toutes les métriques
        metrics = metrics_service.compute_all_metrics(
            predictions=predictions,
            ground_truths=ground_truths,
            class_names=request.class_names,
            iou_threshold=request.iou_threshold
        )
        
        return MetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des métriques: {str(e)}"
        )


@router.get("/model/{model_id}")
async def get_model_metrics(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer les métriques d'un modèle entraîné.
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Modèle introuvable")
    
    # Récupérer les métriques stockées
    stored_metrics = model.metrics or {}
    
    # Enrichir avec des métriques par défaut si manquantes
    response = {
        "model_id": str(model.id),
        "model_name": model.name,
        "version": model.version,
        "basic_metrics": {
            "map50": stored_metrics.get("map50", 0),
            "map50_95": stored_metrics.get("map50_95", 0),
            "precision": stored_metrics.get("precision", 0),
            "recall": stored_metrics.get("recall", 0)
        },
        "extended_metrics": stored_metrics.get("extended_metrics", None),
        "inference_stats": {
            "inference_count": model.inference_count or 0,
            "avg_inference_time_ms": model.avg_inference_time_ms or 0
        }
    }
    
    return response


@router.get("/training/{job_id}")
async def get_training_metrics(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer les métriques d'un job d'entraînement.
    """
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job d'entraînement introuvable")
    
    stored_metrics = job.metrics or {}
    
    response = {
        "job_id": str(job.id),
        "status": job.status,
        "current_epoch": job.current_epoch,
        "progress": job.progress,
        "basic_metrics": {
            "map50": stored_metrics.get("map50", 0),
            "map50_95": stored_metrics.get("map50_95", 0),
            "precision": stored_metrics.get("precision", 0),
            "recall": stored_metrics.get("recall", 0)
        },
        "loss_metrics": {
            "box_loss": stored_metrics.get("box_loss", 0),
            "cls_loss": stored_metrics.get("cls_loss", 0),
            "dfl_loss": stored_metrics.get("dfl_loss", 0)
        },
        "extended_metrics": stored_metrics.get("extended_metrics", None),
        "history": stored_metrics.get("history", [])
    }
    
    return response


@router.get("/calibration-interpretation")
async def get_calibration_interpretation(
    ece_value: float,
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir l'interprétation d'un score ECE.
    """
    if ece_value <= 0.05:
        level = "excellent"
        description = "Le modèle est très bien calibré. Les confiances prédites correspondent fidèlement aux probabilités réelles."
        color = "green"
    elif ece_value <= 0.10:
        level = "bon"
        description = "Le modèle est bien calibré. Les estimations de confiance sont généralement fiables."
        color = "blue"
    elif ece_value <= 0.15:
        level = "modéré"
        description = "Le modèle a une calibration acceptable mais pourrait être amélioré. Certaines confiances peuvent être surestimées ou sous-estimées."
        color = "yellow"
    elif ece_value <= 0.25:
        level = "faible"
        description = "Le modèle est mal calibré. Les confiances ne reflètent pas bien les probabilités réelles. Une recalibraiton est recommandée."
        color = "orange"
    else:
        level = "très faible"
        description = "Le modèle est très mal calibré. Les confiances ne sont pas fiables. Une recalibration ou un réentraînement est nécessaire."
        color = "red"
    
    return {
        "ece": ece_value,
        "level": level,
        "description": description,
        "color": color,
        "recommendation": "Un ECE idéal est < 0.05. Utilisez des techniques comme Temperature Scaling pour améliorer la calibration." if ece_value > 0.10 else None
    }
