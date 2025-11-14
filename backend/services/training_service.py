import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from ultralytics import YOLO
import shutil


class TrainingService:
    """Service pour entraîner des modèles YOLOv8"""
    
    MODELS = {
        "yolov8n": "yolov8n.pt",  # Nano - Plus rapide
        "yolov8s": "yolov8s.pt",  # Small
        "yolov8m": "yolov8m.pt",  # Medium
        "yolov8l": "yolov8l.pt",  # Large - Plus précis
        "yolov8x": "yolov8x.pt",  # XLarge - Le plus précis
    }
    
    def __init__(self, workspace_dir: str = "/tmp/training"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def prepare_dataset(
        self,
        project_id: str,
        images_data: List[Dict],
        classes: List[str],
    ) -> str:
        """Préparer le dataset au format YOLO"""
        
        dataset_dir = os.path.join(self.workspace_dir, project_id)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Créer la structure YOLO
        for split in ["train", "val", "test"]:
            os.makedirs(os.path.join(dataset_dir, "images", split), exist_ok=True)
            os.makedirs(os.path.join(dataset_dir, "labels", split), exist_ok=True)
        
        # Split dataset : 70% train, 20% val, 10% test
        total = len(images_data)
        train_size = int(0.7 * total)
        val_size = int(0.2 * total)
        
        for idx, img in enumerate(images_data):
            if idx < train_size:
                split = "train"
            elif idx < train_size + val_size:
                split = "val"
            else:
                split = "test"
            
            # Copier l'image
            img_dest = os.path.join(dataset_dir, "images", split, img["filename"])
            shutil.copy(img["path"], img_dest)
            
            # Créer le fichier label YOLO
            if img.get("annotations"):
                label_file = os.path.join(
                    dataset_dir,
                    "labels",
                    split,
                    Path(img["filename"]).stem + ".txt"
                )
                
                with open(label_file, "w") as f:
                    for ann in img["annotations"]:
                        class_id = classes.index(ann["class_name"]) if ann["class_name"] in classes else 0
                        
                        # Convertir bbox en format YOLO (x_center, y_center, width, height) normalisé
                        x_center = (ann["bbox"]["x"] + ann["bbox"]["width"] / 2) / img["width"]
                        y_center = (ann["bbox"]["y"] + ann["bbox"]["height"] / 2) / img["height"]
                        width = ann["bbox"]["width"] / img["width"]
                        height = ann["bbox"]["height"] / img["height"]
                        
                        f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")
        
        # Créer data.yaml
        data_yaml = {
            "path": dataset_dir,
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(classes),
            "names": classes
        }
        
        yaml_path = os.path.join(dataset_dir, "data.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(data_yaml, f)
        
        return yaml_path
    
    def train(
        self,
        data_yaml: str,
        model_name: str = "yolov8n",
        epochs: int = 100,
        batch_size: int = 16,
        imgsz: int = 640,
        patience: int = 50,
        project_name: str = "training",
        name: str = "exp",
        **kwargs
    ) -> Dict:
        """Entraîner un modèle YOLOv8"""
        
        if model_name not in self.MODELS:
            raise ValueError(f"Model {model_name} not supported. Choose from {list(self.MODELS.keys())}")
        
        # Charger le modèle pré-entraîné
        model = YOLO(self.MODELS[model_name])
        
        # Entraîner
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            patience=patience,
            project=project_name,
            name=name,
            save=True,
            save_period=10,
            plots=True,
            **kwargs
        )
        
        # Obtenir les métriques
        metrics = {
            "final_metrics": results.results_dict if hasattr(results, 'results_dict') else {},
            "best_model_path": os.path.join(project_name, name, "weights", "best.pt"),
            "last_model_path": os.path.join(project_name, name, "weights", "last.pt"),
        }
        
        return metrics
    
    def validate(self, model_path: str, data_yaml: str) -> Dict:
        """Valider un modèle"""
        model = YOLO(model_path)
        results = model.val(data=data_yaml)
        
        return {
            "map50": float(results.box.map50),
            "map50_95": float(results.box.map),
            "precision": float(results.box.mp),
            "recall": float(results.box.mr),
        }
    
    def cleanup(self, project_id: str):
        """Nettoyer les fichiers temporaires"""
        dataset_dir = os.path.join(self.workspace_dir, project_id)
        if os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir)
