import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import uuid


class DatasetImporter:
    """Service pour importer des datasets (COCO, YOLO, ou simple)"""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    def __init__(self, temp_dir: str = "/tmp/datasets"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def detect_format(self, extract_path: Path) -> str:
        """Détecte le format du dataset (coco, yolo, simple)"""
        
        # Check COCO format (annotations.json ou instances_*.json)
        coco_files = list(extract_path.glob("**/annotations.json")) + \
                     list(extract_path.glob("**/instances_*.json"))
        if coco_files:
            return "coco"
        
        # Check YOLO format (data.yaml + labels/)
        yaml_files = list(extract_path.glob("**/data.yaml"))
        labels_dirs = list(extract_path.glob("**/labels"))
        if yaml_files or labels_dirs:
            return "yolo"
        
        # Simple images
        return "simple"
    
    def extract_zip(self, zip_path: str) -> Path:
        """Extrait le ZIP dans un dossier temporaire"""
        extract_id = str(uuid.uuid4())
        extract_path = Path(self.temp_dir) / extract_id
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        return extract_path
    
    def find_images(self, path: Path) -> List[Path]:
        """Trouve toutes les images dans le dossier"""
        images = []
        for ext in self.SUPPORTED_IMAGE_FORMATS:
            images.extend(path.rglob(f"*{ext}"))
        return images
    
    def parse_coco_annotations(self, coco_json_path: Path) -> Dict:
        """Parse les annotations COCO"""
        with open(coco_json_path, 'r') as f:
            data = json.load(f)
        
        # Créer un mapping image_id -> annotations
        annotations_by_image = {}
        for ann in data.get('annotations', []):
            image_id = ann['image_id']
            if image_id not in annotations_by_image:
                annotations_by_image[image_id] = []
            annotations_by_image[image_id].append(ann)
        
        # Créer un mapping category_id -> name
        categories = {cat['id']: cat['name'] for cat in data.get('categories', [])}
        
        # Créer un mapping filename -> annotations
        result = {}
        for img in data.get('images', []):
            filename = img['file_name']
            image_id = img['id']
            
            if image_id in annotations_by_image:
                result[filename] = {
                    'width': img['width'],
                    'height': img['height'],
                    'annotations': []
                }
                
                for ann in annotations_by_image[image_id]:
                    bbox = ann['bbox']  # [x, y, width, height]
                    result[filename]['annotations'].append({
                        'class_name': categories.get(ann['category_id'], 'unknown'),
                        'bbox': {
                            'x': bbox[0],
                            'y': bbox[1],
                            'width': bbox[2],
                            'height': bbox[3]
                        }
                    })
        
        return result
    
    def parse_yolo_annotations(self, labels_dir: Path, images: List[Path]) -> Dict:
        """Parse les annotations YOLO"""
        result = {}
        
        for img_path in images:
            # Chercher le fichier .txt correspondant
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            if label_path.exists():
                with open(label_path, 'r') as f:
                    lines = f.readlines()
                
                # Pour YOLO, on a besoin des dimensions de l'image
                # On va les stocker pour plus tard
                result[img_path.name] = {
                    'annotations': [],
                    'yolo_format': True  # Flag pour conversion plus tard
                }
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id, x_center, y_center, width, height = parts
                        result[img_path.name]['annotations'].append({
                            'class_id': int(class_id),
                            'bbox_normalized': {
                                'x_center': float(x_center),
                                'y_center': float(y_center),
                                'width': float(width),
                                'height': float(height)
                            }
                        })
        
        return result
    
    def analyze_dataset(self, zip_path: str) -> Dict:
        """Analyse un dataset ZIP et retourne les infos"""
        extract_path = self.extract_zip(zip_path)
        
        format_type = self.detect_format(extract_path)
        images = self.find_images(extract_path)
        
        result = {
            'format': format_type,
            'total_images': len(images),
            'extract_path': str(extract_path),
            'has_annotations': format_type in ['coco', 'yolo'],
            'classes': []
        }
        
        if format_type == 'coco':
            coco_files = list(extract_path.glob("**/annotations.json")) + \
                        list(extract_path.glob("**/instances_*.json"))
            if coco_files:
                with open(coco_files[0], 'r') as f:
                    data = json.load(f)
                result['classes'] = [cat['name'] for cat in data.get('categories', [])]
                result['annotated_images'] = len([img for img in data.get('images', []) 
                                                  if img['id'] in [ann['image_id'] 
                                                  for ann in data.get('annotations', [])]])
        
        elif format_type == 'yolo':
            labels_dirs = list(extract_path.glob("**/labels"))
            if labels_dirs:
                label_files = list(labels_dirs[0].glob("*.txt"))
                result['annotated_images'] = len(label_files)
        
        return result
    
    def cleanup(self, extract_path: str):
        """Nettoie le dossier temporaire"""
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
