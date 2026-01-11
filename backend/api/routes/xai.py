"""
Routes API pour XAI (Explainable AI).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from api.dependencies import get_db, get_current_user
from models.user import User
from models.model import Model
from models.prediction import Prediction
from services.xai.xai_service import create_xai_service
from services.inference import inference_service

router = APIRouter()


class XAIRequest(BaseModel):
    """Requête pour générer des explications XAI."""
    image_path: str
    methods: Optional[List[str]] = ["gradcam"]
    model_id: Optional[str] = None
    bbox: Optional[List[float]] = None  # Bounding box pour focus [x1, y1, x2, y2]


class XAIExplanation(BaseModel):
    """Structure d'une explication XAI."""
    method: str
    heatmap: Optional[str] = None
    success: bool
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None
    interpretation: Optional[str] = None


class XAIResponse(BaseModel):
    """Réponse contenant les explications XAI."""
    explanations: dict
    image_path: str
    model_id: Optional[str] = None
    total_processing_time_ms: Optional[float] = None


@router.post("/api/xai/generate", response_model=XAIResponse)
async def generate_xai_explanations(
    request: XAIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Génère des explications XAI pour une image donnée.
    
    Méthodes disponibles:
    - gradcam: Grad-CAM (Gradient-weighted Class Activation Mapping)
    - gradcam++: Grad-CAM++ (amélioration de Grad-CAM)
    - lime: LIME (Local Interpretable Model-agnostic Explanations)
    - integrated_gradients: Integrated Gradients (Captum)
    - shap: SHAP (SHapley Additive exPlanations)
    """
    try:
        # Récupérer le modèle
        if request.model_id:
            model = db.query(Model).filter(Model.id == request.model_id).first()
            if not model:
                raise HTTPException(status_code=404, detail="Model not found")
            # Télécharger le modèle depuis MinIO
            model_path = inference_service.download_model_from_minio(
                model.storage_path,
                str(model.id)
            )
        else:
            # Utiliser le modèle par défaut (yolov8n)
            model_path = "/app/yolov8n.pt"
        
        # Créer le service XAI
        xai_service = create_xai_service(model_path)
        
        # Générer toutes les explications demandées
        all_results = xai_service.generate_all_explanations(
            request.image_path,
            methods=request.methods
        )
        
        return XAIResponse(
            explanations=all_results["explanations"],
            image_path=request.image_path,
            model_id=request.model_id,
            total_processing_time_ms=all_results.get("total_processing_time_ms")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XAI generation failed: {str(e)}")


@router.get("/api/xai/methods")
async def list_xai_methods(
    current_user: User = Depends(get_current_user),
):
    """
    Liste les méthodes XAI disponibles avec leur statut.
    
    Retourne la liste des méthodes, leur disponibilité (selon les dépendances installées),
    leur vitesse estimée et une description.
    """
    # Créer un service temporaire pour obtenir les méthodes disponibles
    # On utilise un modèle dummy car on veut juste les infos statiques
    try:
        # Essayer de créer le service pour obtenir les vraies disponibilités
        import os
        model_path = "/app/yolov8n.pt"
        if not os.path.exists(model_path):
            model_path = "yolov8n.pt"  # Fallback
        
        xai_service = create_xai_service(model_path)
        methods = xai_service.get_available_methods()
    except Exception:
        # Fallback avec des valeurs par défaut
        methods = [
            {
                "id": "gradcam",
                "name": "Grad-CAM",
                "description": "Gradient-weighted Class Activation Mapping - Visualise les zones importantes",
                "available": True,
                "speed": "fast",
                "recommended": True
            },
            {
                "id": "gradcam++",
                "name": "Grad-CAM++",
                "description": "Version améliorée de Grad-CAM avec meilleure localisation",
                "available": True,
                "speed": "fast",
                "recommended": True
            },
            {
                "id": "lime",
                "name": "LIME",
                "description": "Local Interpretable Model-agnostic Explanations - Explications par super-pixels",
                "available": True,
                "speed": "medium",
                "recommended": True
            },
            {
                "id": "shap",
                "name": "SHAP",
                "description": "SHapley Additive exPlanations - Basé sur la théorie des jeux",
                "available": True,
                "speed": "slow",
                "recommended": False
            },
            {
                "id": "integrated_gradients",
                "name": "Integrated Gradients",
                "description": "Attribution par intégration des gradients",
                "available": True,
                "speed": "medium",
                "recommended": True
            }
        ]
    
    return {"methods": methods}


@router.get("/api/predictions/{prediction_id}/xai")
async def get_prediction_xai(
    prediction_id: str,
    methods: List[str] = Query(default=["gradcam"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Génère des explications XAI pour une prédiction existante."""
    # Récupérer la prédiction
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Générer les explications
    request = XAIRequest(
        image_path=prediction.image_path,
        methods=methods,
        model_id=str(prediction.model_id)
    )
    
    return await generate_xai_explanations(request, db, current_user)


@router.post("/api/xai/compare")
async def compare_xai_methods(
    request: XAIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compare plusieurs méthodes XAI pour la même image.
    
    Génère toutes les méthodes demandées et retourne une comparaison
    avec les temps de traitement et les visualisations.
    """
    # Par défaut, comparer les méthodes les plus utiles
    if not request.methods or len(request.methods) == 0:
        request.methods = ["gradcam", "lime", "integrated_gradients"]
    
    return await generate_xai_explanations(request, db, current_user)
