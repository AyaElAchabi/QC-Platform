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
        if not GRADCAM_AVAILABLE:
            return {
                "error": "Grad-CAM not available. Install pytorch_grad_cam.",
                "heatmap": None,
                "success": False
            }

        start_time = time.time()

        try:
            # Prétraiter l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)

            # Obtenir le modèle PyTorch sous-jacent
            pytorch_model = self.model.model

            # Sélectionner la couche cible (dernière couche conv par défaut)
            if target_layer is None:
                target_layers = [pytorch_model.model[-2]]
            else:
                target_layers = [pytorch_model.model[-2]]

            # Sélectionner la méthode Grad-CAM
            if method == "gradcam++":
                cam = GradCAMPlusPlus(model=pytorch_model, target_layers=target_layers)
            elif method == "eigencam":
                cam = EigenCAM(model=pytorch_model, target_layers=target_layers)
            else:
                cam = GradCAM(model=pytorch_model, target_layers=target_layers)

            # Générer la heatmap
            grayscale_cam = cam(input_tensor=image_tensor)
            grayscale_cam = grayscale_cam[0, :]

            # Superposer la heatmap sur l'image
            visualization = show_cam_on_image(image_normalized, grayscale_cam, use_rgb=True)

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": method,
                "heatmap": heatmap_base64,
                "target_layer": str(target_layers[0]),
                "processing_time_ms": round(processing_time_ms, 2),
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Grad-CAM generation failed: {str(e)}",
                "heatmap": None,
                "success": False
            }

    def generate_lime(
        self,
        image_path: str,
        num_samples: int = 500,
        num_features: int = 10
    ) -> Dict[str, Any]:
        """
        Génère une explication LIME pour une image.

        LIME (Local Interpretable Model-agnostic Explanations) crée des 
        super-pixels et perturbe l'image pour comprendre quelles régions
        sont les plus importantes pour la prédiction.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            num_samples: Nombre de perturbations à générer
            num_features: Nombre de features (superpixels) à montrer

        Returns:
            Dict contenant l'explication encodée en base64
        """
        if not LIME_AVAILABLE:
            return {
                "error": "LIME not available. Install with: pip install lime scikit-image",
                "heatmap": None,
                "success": False
            }

        start_time = time.time()

        try:
            # Charger l'image
            if image_path.startswith("data:image"):
                header, base64_data = image_path.split(",", 1)
                image_bytes = base64.b64decode(base64_data)
                image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            else:
                image_pil = Image.open(image_path).convert("RGB")

            image_np = np.array(image_pil)
            image_resized = cv2.resize(image_np, (640, 640))

            # Fonction de prédiction pour LIME
            def predict_fn(images):
                """Fonction de batch prediction pour LIME."""
                batch_predictions = []
                for img in images:
                    # Prédiction YOLO
                    results = self.model.predict(img, verbose=False)[0]
                    
                    # Calculer un score basé sur les détections
                    if results.boxes is not None and len(results.boxes) > 0:
                        # Moyenne des confiances pondérée par la taille des boîtes
                        confs = results.boxes.conf.cpu().numpy()
                        score = np.max(confs) if len(confs) > 0 else 0
                    else:
                        score = 0
                    
                    # Retourner comme probabilités binaires [pas de défaut, défaut]
                    batch_predictions.append([1 - score, score])
                
                return np.array(batch_predictions)

            # Créer l'explainer LIME
            explainer = lime_image.LimeImageExplainer()

            # Générer l'explication
            explanation = explainer.explain_instance(
                image_resized,
                predict_fn,
                top_labels=1,
                hide_color=0,
                num_samples=num_samples,
                segmentation_fn=lambda x: quickshift(x, kernel_size=4, max_dist=200, ratio=0.2)
            )

            # Obtenir l'image avec les superpixels positifs/négatifs
            temp, mask = explanation.get_image_and_mask(
                explanation.top_labels[0],
                positive_only=False,
                num_features=num_features,
                hide_rest=False
            )

            # Créer une visualisation avec couleurs
            # Vert = contribution positive, Rouge = contribution négative
            visualization = temp.copy()
            
            # Appliquer un overlay coloré basé sur le masque
            overlay = np.zeros_like(visualization, dtype=np.float32)
            overlay[mask == 1] = [0, 255, 0]  # Vert pour positif
            overlay[mask == -1] = [255, 0, 0]  # Rouge pour négatif
            
            # Blend
            alpha = 0.4
            visualization = cv2.addWeighted(
                visualization.astype(np.float32), 1 - alpha,
                overlay, alpha, 0
            ).astype(np.uint8)

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "lime",
                "heatmap": heatmap_base64,
                "num_samples": num_samples,
                "num_features": num_features,
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Vert = régions contribuant à la détection. Rouge = régions qui s'opposent à la détection.",
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
        Génère une explication SHAP pour une image.

        SHAP (SHapley Additive exPlanations) utilise la théorie des jeux
        pour attribuer une importance à chaque pixel.

        Args:
            image_path: Chemin vers l'image ou data URL base64
            num_samples: Nombre d'échantillons pour l'approximation

        Returns:
            Dict contenant l'explication encodée en base64
        """
        if not SHAP_AVAILABLE:
            return {
                "error": "SHAP not available. Install with: pip install shap",
                "heatmap": None,
                "success": False
            }

        start_time = time.time()

        try:
            # Charger l'image
            if image_path.startswith("data:image"):
                header, base64_data = image_path.split(",", 1)
                image_bytes = base64.b64decode(base64_data)
                image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            else:
                image_pil = Image.open(image_path).convert("RGB")

            image_np = np.array(image_pil)
            image_resized = cv2.resize(image_np, (224, 224))  # Plus petit pour SHAP
            
            # Normaliser
            image_normalized = image_resized.astype(np.float32) / 255.0

            # Fonction de prédiction pour SHAP
            def predict_fn(images):
                """Fonction wrapper pour SHAP."""
                predictions = []
                for img in images:
                    # Dénormaliser et resize pour YOLO
                    img_uint8 = (img * 255).astype(np.uint8)
                    img_640 = cv2.resize(img_uint8, (640, 640))
                    
                    results = self.model.predict(img_640, verbose=False)[0]
                    
                    if results.boxes is not None and len(results.boxes) > 0:
                        score = float(results.boxes.conf.cpu().numpy().max())
                    else:
                        score = 0.0
                    
                    predictions.append(score)
                
                return np.array(predictions)

            # Créer un masker basé sur l'image moyenne
            masker = shap.maskers.Image("blur(64,64)", image_normalized.shape)

            # Créer l'explainer
            explainer = shap.Explainer(predict_fn, masker, output_names=["defect_score"])

            # Générer les valeurs SHAP
            shap_values = explainer(
                np.expand_dims(image_normalized, 0),
                max_evals=num_samples,
                batch_size=10
            )

            # Obtenir les valeurs SHAP pour la première image
            shap_image = shap_values.values[0]
            
            # Créer une heatmap à partir des valeurs SHAP
            # Prendre la somme absolue sur les canaux RGB
            shap_heatmap = np.abs(shap_image).sum(axis=-1)
            
            # Normaliser
            if shap_heatmap.max() > 0:
                shap_heatmap = shap_heatmap / shap_heatmap.max()

            # Appliquer une colormap
            shap_heatmap_colored = cv2.applyColorMap(
                (shap_heatmap * 255).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            shap_heatmap_colored = cv2.cvtColor(shap_heatmap_colored, cv2.COLOR_BGR2RGB)

            # Superposer sur l'image originale
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            visualization = cv2.addWeighted(
                image_uint8, 0.5,
                shap_heatmap_colored, 0.5, 0
            )

            # Resize to 640x640 for consistency
            visualization = cv2.resize(visualization, (640, 640))

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "shap",
                "heatmap": heatmap_base64,
                "num_samples": num_samples,
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Les zones colorées montrent l'importance de chaque région pour la détection. Rouge/jaune = haute importance.",
                "success": True
            }

        except Exception as e:
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
        if not CAPTUM_AVAILABLE:
            return {
                "error": "Captum not available. Install with: pip install captum",
                "heatmap": None,
                "success": False
            }

        start_time = time.time()

        try:
            # Charger l'image
            image_normalized, image_tensor = self.preprocess_image(image_path)

            # Obtenir le modèle PyTorch
            pytorch_model = self.model.model.eval()

            # Créer une fonction forward simplifiée qui retourne un score scalaire
            class ModelWrapper(torch.nn.Module):
                def __init__(self, yolo_model):
                    super().__init__()
                    self.model = yolo_model

                def forward(self, x):
                    # Forward pass through YOLO backbone
                    outputs = self.model(x)
                    
                    # Pour YOLO, on prend la moyenne des activations comme proxy
                    if isinstance(outputs, (list, tuple)):
                        # Prendre le dernier output
                        out = outputs[-1] if isinstance(outputs[-1], torch.Tensor) else outputs[0]
                    else:
                        out = outputs
                    
                    # Réduire à un scalaire
                    if out.dim() > 1:
                        return out.mean(dim=tuple(range(1, out.dim())))
                    return out

            wrapped_model = ModelWrapper(pytorch_model)
            wrapped_model.to(self.device)
            wrapped_model.eval()

            # Créer l'explainer Integrated Gradients
            ig = IntegratedGradients(wrapped_model)

            # Baseline = image noire
            baseline = torch.zeros_like(image_tensor)

            # Calculer les attributions
            image_tensor.requires_grad = True
            
            attributions = ig.attribute(
                image_tensor,
                baselines=baseline,
                n_steps=n_steps,
                return_convergence_delta=False
            )

            # Convertir en numpy
            attr_np = attributions.squeeze().cpu().detach().numpy()
            
            # Prendre la valeur absolue et sommer sur les canaux
            attr_sum = np.abs(attr_np).sum(axis=0)
            
            # Normaliser
            if attr_sum.max() > 0:
                attr_sum = attr_sum / attr_sum.max()

            # Appliquer une colormap
            attr_colored = cv2.applyColorMap(
                (attr_sum * 255).astype(np.uint8),
                cv2.COLORMAP_INFERNO
            )
            attr_colored = cv2.cvtColor(attr_colored, cv2.COLOR_BGR2RGB)

            # Superposer sur l'image originale
            image_uint8 = (image_normalized * 255).astype(np.uint8)
            visualization = cv2.addWeighted(
                image_uint8, 0.5,
                attr_colored, 0.5, 0
            )

            # Encoder en base64
            heatmap_base64 = self._encode_image_to_base64(visualization)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                "method": "integrated_gradients",
                "heatmap": heatmap_base64,
                "n_steps": n_steps,
                "processing_time_ms": round(processing_time_ms, 2),
                "interpretation": "Les zones claires indiquent les pixels ayant le plus contribué à la détection du défaut.",
                "success": True
            }

        except Exception as e:
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
