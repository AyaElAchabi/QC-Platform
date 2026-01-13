"""
SAM Segmentation Service
Uses FastSAM with YOLOv8 detection bboxes as prompts
"""
from ultralytics import FastSAM
from PIL import Image
import numpy as np
import base64
import io
import cv2
from typing import List, Dict, Tuple, Optional
import os


class SAMSegmentationService:
    """Service pour la segmentation avec FastSAM"""
    
    def __init__(self):
        self.model = None
        self.model_path = "FastSAM-s.pt"  # Smaller, faster model
        
    def _ensure_model_loaded(self):
        """Charge le modèle FastSAM si nécessaire"""
        if self.model is None:
            # FastSAM-s est plus léger (~23MB) vs FastSAM-x (~138MB)
            self.model = FastSAM(self.model_path)
            print(f"FastSAM model loaded: {self.model_path}")
    
    def segment_with_bboxes(
        self,
        image: Image.Image,
        detections: List[Dict],
        colors: Optional[List[Tuple[int, int, int]]] = None
    ) -> Dict:
        """
        Segmente l'image en utilisant les bounding boxes comme prompts.
        
        Args:
            image: Image PIL
            detections: Liste des détections avec 'bbox' et 'class_name'
            colors: Couleurs optionnelles pour chaque classe
        
        Returns:
            Dict avec 'annotated_image' (base64) et 'masks' (liste)
        """
        self._ensure_model_loaded()
        
        # Convertir PIL en numpy
        img_np = np.array(image)
        if len(img_np.shape) == 2:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
        elif img_np.shape[2] == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
        
        # Couleurs par défaut - rouges/oranges pour les défauts
        default_colors = [
            (255, 50, 50),    # Rouge
            (255, 100, 50),   # Orange-rouge
            (255, 150, 50),   # Orange
            (200, 50, 50),    # Rouge foncé
            (255, 80, 80),    # Rouge clair
        ]
        
        if colors is None:
            colors = default_colors
        
        # Image de sortie avec overlay
        overlay = img_np.copy()
        mask_data = []
        
        if not detections:
            # Pas de détections, retourner l'image originale
            return self._prepare_output(img_np, [])
        
        # Préparer les bboxes pour FastSAM
        bboxes = []
        for det in detections:
            bbox = det.get('bbox', [])
            if len(bbox) == 4:
                # Format [x1, y1, x2, y2]
                bboxes.append(bbox)
        
        if not bboxes:
            return self._prepare_output(img_np, [])
        
        try:
            # Exécuter FastSAM avec prompts bboxes
            results = self.model(
                img_np,
                device='cpu',  # Utiliser CPU pour compatibilité
                retina_masks=True,
                imgsz=640,
                conf=0.4,
                iou=0.9,
            )
            
            # Obtenir les masques pour chaque bbox
            if results and len(results) > 0:
                result = results[0]
                
                # Pour chaque détection, trouver le masque correspondant
                for idx, det in enumerate(detections):
                    bbox = det.get('bbox', [])
                    if len(bbox) != 4:
                        continue
                    
                    x1, y1, x2, y2 = [int(v) for v in bbox]
                    color = colors[idx % len(colors)]
                    
                    # Créer un masque approximatif basé sur la bbox
                    # FastSAM peut générer des masques, mais on utilise une approche simplifiée
                    mask = np.zeros((img_np.shape[0], img_np.shape[1]), dtype=np.uint8)
                    
                    # Si FastSAM a des masques, les utiliser
                    if hasattr(result, 'masks') and result.masks is not None:
                        all_masks = result.masks.data.cpu().numpy()
                        
                        # Trouver le masque qui correspond le mieux à cette bbox
                        best_mask_idx = self._find_best_mask(all_masks, bbox, img_np.shape[:2])
                        
                        if best_mask_idx is not None:
                            mask = all_masks[best_mask_idx]
                            # Redimensionner si nécessaire
                            if mask.shape != (img_np.shape[0], img_np.shape[1]):
                                mask = cv2.resize(
                                    mask.astype(np.float32),
                                    (img_np.shape[1], img_np.shape[0])
                                )
                            mask = (mask > 0.5).astype(np.uint8)
                    
                    # Si pas de masque trouvé, créer un masque simple à partir de la bbox
                    if mask.sum() == 0:
                        # Créer un masque elliptique dans la bbox pour une apparence plus naturelle
                        center = ((x1 + x2) // 2, (y1 + y2) // 2)
                        axes = ((x2 - x1) // 2, (y2 - y1) // 2)
                        cv2.ellipse(mask, center, axes, 0, 0, 360, 1, -1)
                    
                    # Appliquer le masque coloré avec transparence
                    mask_bool = mask > 0
                    alpha = 0.5  # Transparence
                    
                    for c in range(3):
                        overlay[:, :, c] = np.where(
                            mask_bool,
                            (1 - alpha) * img_np[:, :, c] + alpha * color[c],
                            overlay[:, :, c]
                        )
                    
                    # Ajouter un contour pour mieux délimiter
                    contours, _ = cv2.findContours(
                        mask.astype(np.uint8),
                        cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE
                    )
                    cv2.drawContours(overlay, contours, -1, color, 2)
                    
                    mask_data.append({
                        'class_name': det.get('class_name', 'unknown'),
                        'confidence': det.get('confidence', 0),
                        'bbox': bbox,
                        'area_pixels': int(mask_bool.sum())
                    })
            
            return self._prepare_output(overlay, mask_data)
            
        except Exception as e:
            print(f"SAM segmentation error: {e}")
            # Fallback: dessiner des overlays simples sur les bboxes
            return self._fallback_overlay(img_np, detections, colors)
    
    def _find_best_mask(
        self,
        masks: np.ndarray,
        bbox: List[float],
        img_shape: Tuple[int, int]
    ) -> Optional[int]:
        """Trouve le masque qui correspond le mieux à la bbox"""
        x1, y1, x2, y2 = [int(v) for v in bbox]
        bbox_area = (x2 - x1) * (y2 - y1)
        
        best_idx = None
        best_iou = 0
        
        for idx, mask in enumerate(masks):
            # Redimensionner si nécessaire
            if mask.shape != img_shape:
                mask = cv2.resize(
                    mask.astype(np.float32),
                    (img_shape[1], img_shape[0])
                )
            
            # Calculer l'overlap avec la bbox
            mask_in_bbox = mask[y1:y2, x1:x2]
            mask_area = (mask > 0.5).sum()
            overlap_area = (mask_in_bbox > 0.5).sum()
            
            if mask_area > 0:
                iou = overlap_area / (mask_area + bbox_area - overlap_area + 1e-6)
                if iou > best_iou and iou > 0.1:
                    best_iou = iou
                    best_idx = idx
        
        return best_idx
    
    def _fallback_overlay(
        self,
        img_np: np.ndarray,
        detections: List[Dict],
        colors: List[Tuple[int, int, int]]
    ) -> Dict:
        """Overlay simple si FastSAM échoue"""
        overlay = img_np.copy()
        mask_data = []
        
        for idx, det in enumerate(detections):
            bbox = det.get('bbox', [])
            if len(bbox) != 4:
                continue
            
            x1, y1, x2, y2 = [int(v) for v in bbox]
            color = colors[idx % len(colors)]
            
            # Créer un masque elliptique
            mask = np.zeros((img_np.shape[0], img_np.shape[1]), dtype=np.uint8)
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            axes = (max(1, (x2 - x1) // 2), max(1, (y2 - y1) // 2))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 1, -1)
            
            # Appliquer avec transparence
            mask_bool = mask > 0
            alpha = 0.5
            
            for c in range(3):
                overlay[:, :, c] = np.where(
                    mask_bool,
                    (1 - alpha) * img_np[:, :, c] + alpha * color[c],
                    overlay[:, :, c]
                )
            
            # Contour
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, color, 2)
            
            mask_data.append({
                'class_name': det.get('class_name', 'unknown'),
                'confidence': det.get('confidence', 0),
                'bbox': bbox,
                'area_pixels': int(mask_bool.sum())
            })
        
        return self._prepare_output(overlay, mask_data)
    
    def _prepare_output(self, image: np.ndarray, mask_data: List[Dict]) -> Dict:
        """Prépare la sortie avec image en base64"""
        # Convertir en RGB si nécessaire (OpenCV utilise BGR)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Encoder en base64
        pil_image = Image.fromarray(image_rgb.astype(np.uint8))
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'annotated_image': f"data:image/png;base64,{img_base64}",
            'masks': mask_data,
            'num_masks': len(mask_data)
        }


# Singleton instance
_sam_service = None

def get_sam_service() -> SAMSegmentationService:
    """Retourne l'instance singleton du service SAM"""
    global _sam_service
    if _sam_service is None:
        _sam_service = SAMSegmentationService()
    return _sam_service
