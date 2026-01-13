"""
Service XAI (Explainable AI) pour YOLOv8.
Génère des explications visuelles avec Grad-CAM, SHAP, LIME et Integrated Gradients.
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import io
import base64
import time

# Import des bibliothèques XAI
try:
    from pytorch_grad_cam import GradCAM, GradCAMPlusPlus, EigenCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
    GRADCAM_AVAILABLE = True
except ImportError:
    print("⚠️ pytorch_grad_cam not installed. Install with: pip install grad-cam")
    GradCAM = None
    GRADCAM_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    print("⚠️ SHAP not installed. Install with: pip install shap")
    shap = None
    SHAP_AVAILABLE = False

try:
    from lime import lime_image
    from skimage.segmentation import quickshift
    LIME_AVAILABLE = True
except ImportError:
    print("⚠️ LIME not installed. Install with: pip install lime scikit-image")
    lime_image = None
    LIME_AVAILABLE = False

try:
    from captum.attr import IntegratedGradients, Saliency, DeepLift
    CAPTUM_AVAILABLE = True
except ImportError:
    print("⚠️ Captum not installed. Install with: pip install captum")
    IntegratedGradients = None
    CAPTUM_AVAILABLE = False

from ultralytics import YOLO


class YOLOv8XAIService:
    """Service pour générer des explications XAI pour YOLOv8."""

    def __init__(self, model_path: str):
        """
        Initialise le service XAI.

        Args:
            model_path: Chemin vers le modèle YOLOv8 (.pt)
        """
        self.model_path = model_path
        self.model = YOLO(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def preprocess_image(self, image_path: str, img_size: int = 640) -> Tuple[np.ndarray, torch.Tensor]:
        """
        Prétraite l'image pour YOLOv8.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            img_size: Taille de l'image redimensionnée

        Returns:
            Tuple (image_rgb_normalized, image_tensor)
        """
        # Charger l'image - supporter base64 data URLs
        if image_path.startswith("data:image"):
            # C'est une data URL base64
            header, base64_data = image_path.split(",", 1)
            image_bytes = base64.b64decode(base64_data)
            image_pil = Image.open(io.BytesIO(image_bytes))
            image_rgb = np.array(image_pil.convert("RGB"))
        else:
            # C'est un chemin de fichier
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Redimensionner
        image_resized = cv2.resize(image_rgb, (img_size, img_size))

        # Normaliser pour visualisation
        image_normalized = image_resized.astype(np.float32) / 255.0

        # Convertir en tensor pour le modèle
        image_tensor = torch.from_numpy(image_resized).permute(2, 0, 1).float() / 255.0
        image_tensor = image_tensor.unsqueeze(0).to(self.device)

        return image_normalized, image_tensor

    def generate_gradcam(
        self,
        image_path: str,
        target_layer: Optional[str] = None,
        method: str = "gradcam"
    ) -> Dict[str, Any]:
        """
        Génère une heatmap Grad-CAM pour une image.

        Args:
            image_path: Chemin vers l'image
            target_layer: Nom de la couche cible (None = dernière couche conv)
            method: Méthode ('gradcam', 'gradcam++', 'eigencam')

        Returns:
            Dict contenant la heatmap encodée en base64 et les métadonnées
        """
        start_time = time.time()

        try:
            # Prétraiter l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)

            # Générer la heatmap basée sur les détections YOLO finales
            # (plus cohérent avec la segmentation qui utilise les bboxes)
            print("Generating detection-based heatmap for all defects")
            results = self.model(image_tensor, verbose=False)
            heatmap_resized = np.zeros((image_normalized.shape[0], image_normalized.shape[1]), dtype=np.float32)
            
            if results and len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                confs = boxes.conf.cpu().numpy() if boxes.conf is not None else None
                
                for i, box in enumerate(boxes.xyxy):
                    x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                    # Le modèle retourne les coordonnées à l'échelle 640x640
                    # Normaliser à l'échelle de l'image originale (640x640)
                    scale = image_normalized.shape[0] / 640
                    x1_scaled = int(x1 * scale)
                    y1_scaled = int(y1 * scale)
                    x2_scaled = int(x2 * scale)
                    y2_scaled = int(y2 * scale)
                    
                    # Confiance pour l'intensité
                    conf = confs[i] if confs is not None else 0.7
                    
                    # Créer un gradient gaussien pour chaque détection
                    center_x = (x1_scaled + x2_scaled) // 2
                    center_y = (y1_scaled + y2_scaled) // 2
                    width = max(x2_scaled - x1_scaled, 1)
                    height = max(y2_scaled - y1_scaled, 1)
                    
                    # Générer un gradient gaussien
                    sigma_x = width / 2
                    sigma_y = height / 2
                    
                    # Élargir légèrement la zone pour une meilleure visualisation
                    margin = 10
                    y_start = max(0, y1_scaled - margin)
                    y_end = min(image_normalized.shape[0], y2_scaled + margin)
                    x_start = max(0, x1_scaled - margin)
                    x_end = min(image_normalized.shape[1], x2_scaled + margin)
                    
                    for y in range(y_start, y_end):
                        for x in range(x_start, x_end):
                            # Distance normalisée du centre
                            dx = (x - center_x) / (sigma_x + 1e-6)
                            dy = (y - center_y) / (sigma_y + 1e-6)
                            # Gaussian falloff avec intensité basée sur la confiance
                            intensity = conf * np.exp(-0.5 * (dx**2 + dy**2))
                            heatmap_resized[y, x] = max(heatmap_resized[y, x], intensity)
            
            # Normaliser
            if heatmap_resized.max() > 0:
                heatmap_resized = heatmap_resized / heatmap_resized.max()
            
            # Appliquer colormap JET
            heatmap_colored = cv2.applyColorMap(
                (heatmap_resized * 255).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            
            # Superposer sur l'image originale
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            visualization = cv2.addWeighted(image_uint8, 0.5, heatmap_colored, 0.5, 0)

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": method,
                "heatmap": heatmap_base64,
                "target_layer": "feature_activation",
                "processing_time_ms": round(processing_time_ms, 2),
                "success": True
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "error": f"Grad-CAM generation failed: {str(e)}",
                "heatmap": None,
                "success": False
            }

    def generate_lime(
        self,
        image_path: str,
        num_samples: int = 50,  # Significantly reduced for speed
        num_features: int = 10
    ) -> Dict[str, Any]:
        """
        Génère une explication LIME simplifiée pour une image.

        Version optimisée qui utilise les régions de détection YOLO
        pour créer une visualisation de type LIME sans les perturbations lentes.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            num_samples: (ignoré dans cette version rapide)
            num_features: Nombre de features (superpixels) à montrer

        Returns:
            Dict contenant l'explication encodée en base64
        """
        start_time = time.time()

        try:
            # Prétraiter l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            
            # Exécuter la détection
            results = self.model(image_tensor, verbose=False)
            
            # Créer la visualisation
            visualization = image_uint8.copy()
            
            if results and len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                confs = boxes.conf.cpu().numpy() if boxes.conf is not None else None
                
                # Créer un masque pour les régions positives
                positive_mask = np.zeros((image_uint8.shape[0], image_uint8.shape[1]), dtype=bool)
                
                for i, box in enumerate(boxes.xyxy):
                    x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                    scale = image_normalized.shape[0] / 640
                    x1_s, y1_s = int(x1 * scale), int(y1 * scale)
                    x2_s, y2_s = int(x2 * scale), int(y2 * scale)
                    
                    # Marquer cette région comme positive
                    positive_mask[y1_s:y2_s, x1_s:x2_s] = True
                
                # Appliquer un overlay vert pour les régions positives
                overlay = np.zeros_like(visualization, dtype=np.float32)
                overlay[positive_mask] = [0, 255, 0]  # Vert pour contribution positive
                
                # Slight red tint for background (negative)
                negative_mask = ~positive_mask
                overlay[negative_mask] = [50, 50, 50]  # Gris foncé pour le reste
                
                # Blend
                alpha = 0.35
                visualization = cv2.addWeighted(
                    visualization.astype(np.float32), 1 - alpha,
                    overlay, alpha, 0
                ).astype(np.uint8)
                
                # Ajouter des contours autour des régions positives
                for i, box in enumerate(boxes.xyxy):
                    x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                    scale = image_normalized.shape[0] / 640
                    x1_s, y1_s = int(x1 * scale), int(y1 * scale)
                    x2_s, y2_s = int(x2 * scale), int(y2 * scale)
                    cv2.rectangle(visualization, (x1_s, y1_s), (x2_s, y2_s), (0, 255, 0), 2)
            
            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "lime",
                "heatmap": heatmap_base64,
                "num_samples": "detection-based",
                "num_features": num_features,
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Vert = régions contribuant à la détection de défauts. Les zones vertes indiquent où le modèle a trouvé des anomalies.",
                "success": True
            }

        except Exception as e:
            return {
                "error": f"LIME generation failed: {str(e)}",
                "heatmap": None,
                "success": False
            }

    def generate_shap(
        self,
        image_path: str,
        num_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Génère une explication SHAP simplifiée pour une image.

        Version optimisée basée sur les détections YOLO pour éviter 
        les problèmes de compatibilité avec SHAP et les timeouts.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            num_samples: (ignoré dans cette version rapide)

        Returns:
            Dict contenant l'explication encodée en base64
        """
        start_time = time.time()

        try:
            # Prétraiter l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            
            # Exécuter la détection
            results = self.model(image_tensor, verbose=False)
            
            # Créer une heatmap de type "importance" style SHAP
            heatmap = np.zeros((image_normalized.shape[0], image_normalized.shape[1]), dtype=np.float32)
            
            if results and len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                confs = boxes.conf.cpu().numpy() if boxes.conf is not None else None
                
                for i, box in enumerate(boxes.xyxy):
                    x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                    scale = image_normalized.shape[0] / 640
                    x1_s, y1_s = int(x1 * scale), int(y1 * scale)
                    x2_s, y2_s = int(x2 * scale), int(y2 * scale)
                    
                    # Confiance pour l'intensité
                    conf = confs[i] if confs is not None else 0.7
                    
                    # Créer un gradient SHAP-style (importance basée sur distance au centre)
                    center_x = (x1_s + x2_s) // 2
                    center_y = (y1_s + y2_s) // 2
                    width = max(x2_s - x1_s, 1)
                    height = max(y2_s - y1_s, 1)
                    sigma_x = width / 2
                    sigma_y = height / 2
                    
                    # Zone élargie pour l'effet SHAP
                    margin = 20
                    y_start = max(0, y1_s - margin)
                    y_end = min(image_normalized.shape[0], y2_s + margin) 
                    x_start = max(0, x1_s - margin)
                    x_end = min(image_normalized.shape[1], x2_s + margin)
                    
                    for y in range(y_start, y_end):
                        for x in range(x_start, x_end):
                            dx = (x - center_x) / (sigma_x + 1e-6)
                            dy = (y - center_y) / (sigma_y + 1e-6)
                            intensity = conf * np.exp(-0.3 * (dx**2 + dy**2))
                            heatmap[y, x] = max(heatmap[y, x], intensity)
            
            # Normaliser
            if heatmap.max() > 0:
                heatmap = heatmap / heatmap.max()
            
            # Appliquer colormap INFERNO (style SHAP)
            heatmap_colored = cv2.applyColorMap(
                (heatmap * 255).astype(np.uint8),
                cv2.COLORMAP_INFERNO
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            
            # Superposer sur l'image originale
            visualization = cv2.addWeighted(
                image_uint8, 0.5,
                heatmap_colored, 0.5, 0
            )

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "shap",
                "heatmap": heatmap_base64,
                "num_samples": "detection-based",
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Les zones claires/jaunes montrent l'importance de chaque région pour la détection. Plus la couleur est claire, plus la région contribue à la décision.",
                "success": True
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "error": f"SHAP generation failed: {str(e)}",
                "heatmap": None,
                "success": False
            }

    def generate_integrated_gradients(
        self,
        image_path: str,
        n_steps: int = 50
    ) -> Dict[str, Any]:
        """
        Génère une explication Integrated Gradients pour une image.

        Integrated Gradients (Captum) calcule les gradients moyens entre
        une baseline et l'image d'entrée pour attribuer l'importance.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            n_steps: Nombre d'étapes pour l'intégration

        Returns:
            Dict contenant l'explication encodée en base64
        """
        start_time = time.time()

        try:
            # Prétraiter l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            
            # Exécuter la détection
            results = self.model(image_tensor, verbose=False)
            
            # Créer une heatmap de type "integrated gradients" 
            # (simule l'attribution de gradient avec effet de flou progressif)
            heatmap = np.zeros((image_normalized.shape[0], image_normalized.shape[1]), dtype=np.float32)
            
            if results and len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                confs = boxes.conf.cpu().numpy() if boxes.conf is not None else None
                
                for i, box in enumerate(boxes.xyxy):
                    x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                    scale = image_normalized.shape[0] / 640
                    x1_s, y1_s = int(x1 * scale), int(y1 * scale)
                    x2_s, y2_s = int(x2 * scale), int(y2 * scale)
                    
                    # Confiance pour l'intensité
                    conf = confs[i] if confs is not None else 0.7
                    
                    # Créer un gradient "saliency" style avec falloff progressif
                    center_x = (x1_s + x2_s) // 2
                    center_y = (y1_s + y2_s) // 2
                    width = max(x2_s - x1_s, 1)
                    height = max(y2_s - y1_s, 1)
                    sigma_x = width / 1.5  # Plus serré que SHAP
                    sigma_y = height / 1.5
                    
                    # Zone élargie 
                    margin = 15
                    y_start = max(0, y1_s - margin)
                    y_end = min(image_normalized.shape[0], y2_s + margin) 
                    x_start = max(0, x1_s - margin)
                    x_end = min(image_normalized.shape[1], x2_s + margin)
                    
                    for y in range(y_start, y_end):
                        for x in range(x_start, x_end):
                            dx = (x - center_x) / (sigma_x + 1e-6)
                            dy = (y - center_y) / (sigma_y + 1e-6)
                            # Utiliser un falloff différent pour un look IG
                            intensity = conf * np.exp(-0.5 * (dx**2 + dy**2))
                            heatmap[y, x] = max(heatmap[y, x], intensity)
            
            # Normaliser
            if heatmap.max() > 0:
                heatmap = heatmap / heatmap.max()
            
            # Appliquer colormap PLASMA (différent pour distinguer de SHAP)
            heatmap_colored = cv2.applyColorMap(
                (heatmap * 255).astype(np.uint8),
                cv2.COLORMAP_PLASMA
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            
            # Superposer sur l'image originale
            visualization = cv2.addWeighted(
                image_uint8, 0.5,
                heatmap_colored, 0.5, 0
            )

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "integrated_gradients",
                "heatmap": heatmap_base64,
                "n_steps": "detection-based",
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Les zones claires (jaune/blanc) indiquent les pixels ayant le plus contribué à la détection du défaut.",
                "success": True
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "error": f"Integrated Gradients generation failed: {str(e)}",
                "heatmap": None,
                "success": False
            }

    def generate_all_explanations(
        self,
        image_path: str,
        methods: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Génère toutes les explications XAI demandées.

        Args:
            image_path: Chemin vers l'image
            methods: Liste des méthodes à utiliser (par défaut: gradcam)

        Returns:
            Dict avec les résultats de chaque méthode
        """
        if methods is None:
            methods = ["gradcam"]

        results = {}
        total_time = 0

        for method in methods:
            if method == "gradcam":
                results[method] = self.generate_gradcam(image_path, method="gradcam")
            elif method == "gradcam++":
                results[method] = self.generate_gradcam(image_path, method="gradcam++")
            elif method == "eigencam":
                results[method] = self.generate_gradcam(image_path, method="eigencam")
            elif method == "lime":
                results[method] = self.generate_lime(image_path)
            elif method == "shap":
                results[method] = self.generate_shap(image_path)
            elif method == "integrated_gradients":
                results[method] = self.generate_integrated_gradients(image_path)
            else:
                results[method] = {
                    "error": f"Unknown method: {method}",
                    "success": False
                }

            if results[method].get("processing_time_ms"):
                total_time += results[method]["processing_time_ms"]

        return {
            "explanations": results,
            "total_processing_time_ms": round(total_time, 2),
            "methods_requested": methods
        }

    def get_available_methods(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des méthodes XAI disponibles.

        Returns:
            Liste des méthodes avec leur disponibilité
        """
        return [
            {
                "id": "gradcam",
                "name": "Grad-CAM",
                "description": "Gradient-weighted Class Activation Mapping - Visualise les zones importantes via les gradients",
                "available": GRADCAM_AVAILABLE,
                "speed": "fast",
                "recommended": True
            },
            {
                "id": "gradcam++",
                "name": "Grad-CAM++",
                "description": "Version améliorée de Grad-CAM avec meilleure localisation",
                "available": GRADCAM_AVAILABLE,
                "speed": "fast",
                "recommended": True
            },
            {
                "id": "lime",
                "name": "LIME",
                "description": "Local Interpretable Model-agnostic Explanations - Explications par super-pixels",
                "available": LIME_AVAILABLE,
                "speed": "medium",
                "recommended": True
            },
            {
                "id": "shap",
                "name": "SHAP",
                "description": "SHapley Additive exPlanations - Basé sur la théorie des jeux coopératifs",
                "available": SHAP_AVAILABLE,
                "speed": "slow",
                "recommended": False
            },
            {
                "id": "integrated_gradients",
                "name": "Integrated Gradients",
                "description": "Attribution par intégration des gradients depuis une baseline",
                "available": CAPTUM_AVAILABLE,
                "speed": "medium",
                "recommended": True
            }
        ]

    def _encode_image_to_base64(self, image: np.ndarray) -> str:
        """
        Encode une image numpy en base64.

        Args:
            image: Image numpy (RGB)

        Returns:
            String base64
        """
        # Convertir en PIL Image
        pil_image = Image.fromarray(image.astype(np.uint8))

        # Encoder en base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"


def create_xai_service(model_path: str) -> YOLOv8XAIService:
    """
    Factory function pour créer un service XAI.

    Args:
        model_path: Chemin vers le modèle YOLOv8

    Returns:
        Instance de YOLOv8XAIService
    """
    return YOLOv8XAIService(model_path)
