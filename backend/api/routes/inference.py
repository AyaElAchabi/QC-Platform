"""
Inference API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Any
from PIL import Image
import io
import uuid
import numpy as np
import base64

try:
    import cv2
except ImportError:
    cv2 = None

from api.dependencies import get_db, get_current_user
from models.user import User
from models.model import Model
from models.prediction import Prediction
from services.inference import inference_service
from services.xai.xai_service import create_xai_service
from pydantic import BaseModel


router = APIRouter(prefix="/api/inference", tags=["inference"])


class PredictionResponse(BaseModel):
    """Schéma de réponse pour les prédictions"""
    prediction_id: str
    model_id: str
    model_name: str
    detections: list
    num_detections: int
    inference_time_ms: float
    confidence_threshold: float
    image_size: dict
    # Segmentation - image with colored overlay masks
    segmented_image: Optional[str] = None  # Base64 encoded image with segmentation
    # XAI (Explainability) fields - optional
    xai_heatmap: Optional[str] = None  # Base64 encoded heatmap overlay
    xai_metrics: Optional[dict] = None  # Explanation metrics


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    image: UploadFile = File(...),
    model_id: str = Form(...),
    confidence_threshold: float = Form(0.25),
    enable_segmentation: bool = Form(True),  # Enabled by default
    enable_xai: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Effectuer une prédiction sur une image avec un modèle entraîné
    
    Args:
        image: Image à analyser (JPEG, PNG)
        model_id: ID du modèle à utiliser
        confidence_threshold: Seuil de confiance (0.1-0.9)
        
    Returns:
        PredictionResponse: Résultats de la prédiction
    """
    # Validation du seuil de confiance
    if not 0.1 <= confidence_threshold <= 0.9:
        raise HTTPException(
            status_code=400,
            detail="Le seuil de confiance doit être entre 0.1 et 0.9"
        )
    
    # Vérifier que le modèle existe
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Modèle {model_id} introuvable"
        )
    
    # Vérifier que le fichier est une image
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (JPEG, PNG)"
        )
    
    try:
        # Lire l'image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convertir en RGB si nécessaire
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        
        # Effectuer l'inférence
        results = inference_service.run_inference(
            storage_path=model.storage_path,
            model_id=str(model.id),
            image=pil_image,
            confidence_threshold=confidence_threshold
        )
        
        # Générer des explications XAI de base si demandé (heatmap + statistiques)
        # Génère même s'il n'y a pas de détections pour expliquer pourquoi
        xai_data = None
        if enable_xai:
            try:
                import tempfile
                import os
                
                # Dimensions de l'image
                img_width = results["image_size"]["width"]
                img_height = results["image_size"]["height"]
                
                # Générer la heatmap Grad-CAM (toujours, même sans détections)
                heatmap_base64 = None
                try:
                    # Sauvegarder l'image temporairement
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                        pil_image.save(tmp_file.name)
                        tmp_path = tmp_file.name

                    # Télécharger le modèle et créer le service XAI
                    model_path = inference_service.download_model_from_minio(
                        model.storage_path,
                        str(model.id)
                    )
                    xai_service = create_xai_service(model_path)

                    # Générer Grad-CAM
                    print(f"Generating Grad-CAM heatmap for path: {tmp_path}")
                    gradcam_result = xai_service.generate_gradcam(tmp_path)
                    print(f"Grad-CAM result: success={gradcam_result.get('success')}, error={gradcam_result.get('error')}")
                    
                    if gradcam_result.get("success"):
                        heatmap_base64 = gradcam_result["heatmap"]
                        print(f"Heatmap generated successfully, length: {len(heatmap_base64) if heatmap_base64 else 0}")
                    else:
                        print(f"Heatmap generation failed: {gradcam_result.get('error')}")

                    # Nettoyer
                    os.remove(tmp_path)
                except Exception as heatmap_error:
                    import traceback
                    print(f"Heatmap generation error: {heatmap_error}")
                    traceback.print_exc()
                    heatmap_base64 = None

                # Calculer les métriques selon qu'il y a des détections ou non
                if len(results["detections"]) > 0:
                    # Avec détections: statistiques complètes
                    confidences = [d["confidence"] for d in results["detections"]]
                    class_counts = {}
                    for d in results["detections"]:
                        class_name = d["class_name"]
                        if class_name not in class_counts:
                            class_counts[class_name] = {"count": 0, "total_confidence": 0}
                        class_counts[class_name]["count"] += 1
                        class_counts[class_name]["total_confidence"] += d["confidence"]

                    class_distribution = {
                        name: {
                            "count": data["count"],
                            "avg_confidence": data["total_confidence"] / data["count"]
                        }
                        for name, data in class_counts.items()
                    }

                    # Distribution spatiale
                    center_count = 0
                    edge_count = 0
                    for d in results["detections"]:
                        bbox = d["bbox"]
                        center_x = (bbox[0] + bbox[2]) / 2
                        center_y = (bbox[1] + bbox[3]) / 2
                        if (0.3 * img_width < center_x < 0.7 * img_width and
                            0.3 * img_height < center_y < 0.7 * img_height):
                            center_count += 1
                        else:
                            edge_count += 1

                    xai_data = {
                        "heatmap": heatmap_base64,
                        "metrics": {
                            "summary": f"{len(results['detections'])} défaut(s) détecté(s) avec confiance moyenne de {np.mean(confidences):.1%}",
                            "confidence_stats": {
                                "mean": float(np.mean(confidences)),
                                "min": float(np.min(confidences)),
                                "max": float(np.max(confidences)),
                                "std": float(np.std(confidences))
                            },
                            "class_distribution": class_distribution,
                            "spatial_distribution": {
                                "center": center_count,
                                "edges": edge_count
                            },
                            "detection_areas": [
                                {
                                    "class": d["class_name"],
                                    "area_percent": ((d["bbox"][2] - d["bbox"][0]) * (d["bbox"][3] - d["bbox"][1])) / (img_width * img_height) * 100,
                                    "confidence": d["confidence"]
                                }
                                for d in results["detections"][:5]
                            ],
                            "explanation_text": f"**Résultat de l'analyse:**\n"
                                              f"Le modèle a détecté {len(results['detections'])} défaut(s) dans l'image.\n\n"
                                              f"**Classes identifiées:** {', '.join(class_counts.keys())}\n"
                                              f"**Distribution spatiale:** {center_count} au centre, {edge_count} sur les bords.\n\n"
                                              f"La carte d'attention (heatmap) montre les zones où le modèle a concentré son analyse. "
                                              f"Les zones rouges/jaunes correspondent aux régions les plus importantes pour la décision."
                        }
                    }
                else:
                    # Sans détections: expliquer pourquoi rien n'a été détecté
                    xai_data = {
                        "heatmap": heatmap_base64,
                        "metrics": {
                            "summary": f"Aucun défaut détecté (seuil: {confidence_threshold:.0%})",
                            "confidence_stats": {
                                "mean": 0,
                                "min": 0,
                                "max": 0,
                                "std": 0
                            },
                            "class_distribution": {},
                            "spatial_distribution": {
                                "center": 0,
                                "edges": 0
                            },
                            "detection_areas": [],
                            "explanation_text": f"**Résultat de l'analyse: Image conforme ✓**\n\n"
                                              f"Le modèle n'a détecté aucun défaut dépassant le seuil de confiance de {confidence_threshold:.0%}.\n\n"
                                              f"**Interprétation de la heatmap:**\n"
                                              f"- Les zones colorées indiquent où le modèle a cherché des défauts potentiels\n"
                                              f"- L'absence de zones très rouges suggère que l'image ne présente pas de caractéristiques de défauts\n"
                                              f"- Les zones bleu/vert ont été analysées mais n'ont pas déclenché de détection\n\n"
                                              f"**Recommandation:** Si vous suspectez un défaut non détecté, essayez de réduire le seuil de confiance."
                        }
                    }
            except Exception as xai_error:
                # XAI non bloquant - log l'erreur mais continue
                print(f"XAI generation error: {xai_error}")
                xai_data = None
        
        # Générer la segmentation avec masques colorés si demandé
        segmented_image_data = None
        if enable_segmentation and len(results["detections"]) > 0:
            try:
                from services.sam_segmentation import get_sam_service
                sam_service = get_sam_service()
                
                # Générer les masques de segmentation
                seg_result = sam_service.segment_with_bboxes(
                    pil_image,
                    results["detections"]
                )
                
                segmented_image_data = seg_result.get("annotated_image")
                print(f"Segmentation generated with {seg_result.get('num_masks', 0)} masks")
                
            except Exception as seg_error:
                print(f"Segmentation error: {seg_error}")
                # Fallback: créer une image annotée simple
                try:
                    img_np = np.array(pil_image)
                    overlay = img_np.copy()
                    
                    # Couleur rouge semi-transparente pour les défauts
                    for det in results["detections"]:
                        bbox = det.get("bbox", [])
                        if len(bbox) == 4:
                            x1, y1, x2, y2 = [int(v) for v in bbox]
                            # Overlay rouge sur la zone du défaut
                            alpha = 0.4
                            color = (255, 50, 50)  # Rouge
                            overlay[y1:y2, x1:x2, 0] = np.clip(
                                overlay[y1:y2, x1:x2, 0] * (1-alpha) + color[0] * alpha, 0, 255
                            )
                            overlay[y1:y2, x1:x2, 1] = np.clip(
                                overlay[y1:y2, x1:x2, 1] * (1-alpha) + color[1] * alpha, 0, 255
                            )
                            overlay[y1:y2, x1:x2, 2] = np.clip(
                                overlay[y1:y2, x1:x2, 2] * (1-alpha) + color[2] * alpha, 0, 255
                            )
                            # Contour
                            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                    
                    # Encoder en base64
                    from PIL import Image as PILImage
                    pil_overlay = PILImage.fromarray(overlay.astype(np.uint8))
                    buffer = io.BytesIO()
                    pil_overlay.save(buffer, format='PNG')
                    segmented_image_data = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
                except Exception as fallback_error:
                    print(f"Fallback segmentation error: {fallback_error}")
                    segmented_image_data = None
        
        # Sauvegarder la prédiction dans la base de données
        prediction = Prediction(
            id=uuid.uuid4(),
            user_id=current_user.id,
            model_id=model.id,
            results=results,
            inference_time_ms=results["inference_time_ms"],
            confidence_threshold=confidence_threshold
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        # Mettre à jour les statistiques du modèle
        model.inference_count = (model.inference_count or 0) + 1
        
        # Calculer le temps d'inférence moyen
        if model.avg_inference_time_ms is None:
            model.avg_inference_time_ms = results["inference_time_ms"]
        else:
            # Moyenne mobile
            total_time = model.avg_inference_time_ms * (model.inference_count - 1)
            model.avg_inference_time_ms = (total_time + results["inference_time_ms"]) / model.inference_count
        
        db.commit()
        
        # Préparer la réponse
        return PredictionResponse(
            prediction_id=str(prediction.id),
            model_id=str(model.id),
            model_name=model.name,
            detections=results["detections"],
            num_detections=results["num_detections"],
            inference_time_ms=results["inference_time_ms"],
            confidence_threshold=confidence_threshold,
            image_size=results["image_size"],
            segmented_image=segmented_image_data,
            xai_heatmap=xai_data["heatmap"] if xai_data else None,
            xai_metrics=xai_data["metrics"] if xai_data else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'inférence: {str(e)}"
        )


@router.get("/history")
async def get_prediction_history(
    limit: int = 50,
    model_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer l'historique des prédictions de l'utilisateur
    
    Args:
        limit: Nombre maximum de résultats
        model_id: Filtrer par modèle (optionnel)
        
    Returns:
        List: Historique des prédictions
    """
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    
    if model_id:
        query = query.filter(Prediction.model_id == model_id)
    
    predictions = query.order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": str(p.id),
            "model_id": str(p.model_id),
            "num_detections": p.results.get("num_detections", 0),
            "inference_time_ms": p.inference_time_ms,
            "confidence_threshold": p.confidence_threshold,
            "created_at": p.created_at.isoformat()
        }
        for p in predictions
    ]


@router.get("/stats")
async def get_inference_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiques d'inférence globales
    
    Returns:
        Dict: Statistiques
    """
    from sqlalchemy import func
    
    total_predictions = db.query(func.count(Prediction.id)).filter(
        Prediction.user_id == current_user.id
    ).scalar() or 0
    
    avg_inference_time = db.query(func.avg(Prediction.inference_time_ms)).filter(
        Prediction.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "total_predictions": total_predictions,
        "avg_inference_time_ms": round(float(avg_inference_time), 2) if avg_inference_time else 0
    }
