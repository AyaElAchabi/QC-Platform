"""
Inference Service - YOLOv8 Model Loading and Prediction
"""
import time
import io
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple
from ultralytics import YOLO
import tempfile
import os

from core.minio_client import minio_client
from core.redis_client import redis_client


class InferenceService:
    """Service pour gérer les inférences YOLOv8"""
    
    def __init__(self):
        self.models_cache = {}  # Cache mémoire des modèles chargés
        self.cache_ttl = 3600  # 1 heure
    
    def _get_cached_model_path(self, model_id: str) -> Optional[str]:
        """Vérifier si le modèle est en cache Redis"""
        cache_key = f"model_path:{model_id}"
        cached_path = redis_client.get(cache_key)
        
        if cached_path and os.path.exists(cached_path):
            return cached_path
        return None
    
    def _cache_model_path(self, model_id: str, local_path: str):
        """Mettre en cache le chemin du modèle"""
        cache_key = f"model_path:{model_id}"
        redis_client.set(cache_key, local_path, ttl=self.cache_ttl)
    
    def download_model_from_minio(self, storage_path: str, model_id: str) -> str:
        """
        Télécharger le modèle depuis MinIO et le sauvegarder localement
        
        Args:
            storage_path: Chemin dans MinIO (ex: models/project_id/job_id_best.pt)
            model_id: ID unique du modèle
            
        Returns:
            str: Chemin local du modèle téléchargé
        """
        # Vérifier le cache
        cached_path = self._get_cached_model_path(model_id)
        if cached_path:
            return cached_path
        
        # Créer un répertoire temporaire pour stocker les modèles
        models_dir = "/tmp/mlops_models"
        os.makedirs(models_dir, exist_ok=True)
        
        # Nom de fichier local
        local_filename = f"{model_id}.pt"
        local_path = os.path.join(models_dir, local_filename)
        
        # Si le fichier existe déjà localement, le retourner
        if os.path.exists(local_path):
            self._cache_model_path(model_id, local_path)
            return local_path
        
        # Télécharger depuis MinIO
        try:
            # Utiliser le client MinIO sous-jacent
            response = minio_client.client.get_object(
                bucket_name="mlops-models",
                object_name=storage_path
            )
            
            # Écrire le contenu dans le fichier local
            with open(local_path, 'wb') as f:
                for data in response.stream(32*1024):
                    f.write(data)
            
            response.close()
            response.release_conn()
            
            # Mettre en cache
            self._cache_model_path(model_id, local_path)
            return local_path
            
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement du modèle depuis MinIO: {str(e)}")
    
    def load_model(self, model_path: str, model_id: str) -> YOLO:
        """
        Charger un modèle YOLOv8 avec cache mémoire
        
        Args:
            model_path: Chemin local du modèle
            model_id: ID du modèle pour le cache
            
        Returns:
            YOLO: Instance du modèle chargé
        """
        # Vérifier le cache mémoire
        if model_id in self.models_cache:
            return self.models_cache[model_id]
        
        # Charger le modèle
        try:
            model = YOLO(model_path)
            
            # Mettre en cache (limiter à 3 modèles max pour éviter la saturation mémoire)
            if len(self.models_cache) >= 3:
                # Supprimer le plus ancien
                oldest_key = list(self.models_cache.keys())[0]
                del self.models_cache[oldest_key]
            
            self.models_cache[model_id] = model
            return model
            
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du modèle: {str(e)}")
    
    def predict(
        self,
        model: YOLO,
        image: Image.Image,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ) -> Tuple[List[Dict], float]:
        """
        Effectuer une prédiction sur une image
        
        Args:
            model: Modèle YOLO chargé
            image: Image PIL
            confidence_threshold: Seuil de confiance minimum
            iou_threshold: Seuil IoU pour NMS
            
        Returns:
            Tuple[List[Dict], float]: (détections, temps_inference_ms)
        """
        # Convertir PIL Image en numpy array
        img_array = np.array(image)
        
        # Mesurer le temps d'inférence
        start_time = time.time()
        
        # Prédiction
        results = model.predict(
            img_array,
            conf=confidence_threshold,
            iou=iou_threshold,
            verbose=False
        )[0]
        
        inference_time_ms = (time.time() - start_time) * 1000
        
        # Parser les résultats
        detections = []
        
        if results.boxes is not None and len(results.boxes) > 0:
            for i, box in enumerate(results.boxes):
                # Coordonnées du bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                
                # Classe et confiance
                class_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                
                # Nom de la classe
                class_name = results.names[class_id]
                
                detection = {
                    "bbox": [
                        float(x1),
                        float(y1),
                        float(x2),
                        float(y2)
                    ],
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence
                }
                
                detections.append(detection)
        
        return detections, inference_time_ms
    
    def run_inference(
        self,
        storage_path: str,
        model_id: str,
        image: Image.Image,
        confidence_threshold: float = 0.25
    ) -> Dict:
        """
        Pipeline complet d'inférence
        
        Args:
            storage_path: Chemin MinIO du modèle
            model_id: ID du modèle
            image: Image PIL
            confidence_threshold: Seuil de confiance
            
        Returns:
            Dict: Résultats avec détections et métadonnées
        """
        # 1. Télécharger le modèle depuis MinIO
        model_path = self.download_model_from_minio(storage_path, model_id)
        
        # 2. Charger le modèle
        model = self.load_model(model_path, model_id)
        
        # 3. Prédiction
        detections, inference_time_ms = self.predict(
            model,
            image,
            confidence_threshold=confidence_threshold
        )
        
        # 4. Préparer les résultats
        results = {
            "detections": detections,
            "num_detections": len(detections),
            "inference_time_ms": round(inference_time_ms, 2),
            "image_size": {
                "width": image.width,
                "height": image.height
            },
            "confidence_threshold": confidence_threshold
        }
        
        return results


# Instance singleton
inference_service = InferenceService()
