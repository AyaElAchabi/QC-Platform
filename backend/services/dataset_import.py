import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import xml.etree.ElementTree as ET
from PIL import Image


class DatasetImporter:
    """Import datasets in multiple formats"""
    
    SUPPORTED_FORMATS = ["coco", "yolo", "voc", "simple"]
    
    def __init__(self, temp_dir: str = "/tmp/dataset_imports"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def detect_format(self, extract_path: str) -> str:
        """Auto-detect dataset format"""
        
        # Check for COCO format
        if os.path.exists(os.path.join(extract_path, "annotations.json")):
            return "coco"
        
        # Check for YOLO format
        yaml_files = list(Path(extract_path).rglob("*.yaml")) + list(Path(extract_path).rglob("*.yml"))
        txt_files = list(Path(extract_path).rglob("*.txt"))
        if yaml_files and txt_files:
            return "yolo"
        
        # Check for Pascal VOC format
        xml_files = list(Path(extract_path).rglob("*.xml"))
        if xml_files:
            return "voc"
        
        # Default: simple image folder
        return "simple"
    
    def extract_zip(self, zip_path: str, project_id: str) -> str:
        """Extract ZIP file"""
        extract_path = os.path.join(self.temp_dir, project_id)
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        return extract_path
    
    def parse_coco(self, extract_path: str) -> Tuple[List[Dict], Dict]:
        """Parse COCO format"""
        annotations_file = os.path.join(extract_path, "annotations.json")
        
        with open(annotations_file, 'r') as f:
            coco_data = json.load(f)
        
        # Build class mapping
        classes = {cat['id']: cat['name'] for cat in coco_data.get('categories', [])}
        
        # Build image annotations mapping
        image_annotations = {}
        for ann in coco_data.get('annotations', []):
            image_id = ann['image_id']
            if image_id not in image_annotations:
                image_annotations[image_id] = []
            
            bbox = ann['bbox']  # [x, y, width, height]
            image_annotations[image_id].append({
                'class_name': classes.get(ann['category_id'], 'unknown'),
                'bbox': {
                    'x': bbox[0],
                    'y': bbox[1],
                    'width': bbox[2],
                    'height': bbox[3]
                }
            })
        
        # Prepare images data
        images_data = []
        for img in coco_data.get('images', []):
            img_path = self._find_image_file(extract_path, img['file_name'])
            if img_path:
                images_data.append({
                    'filename': img['file_name'],
                    'path': img_path,
                    'width': img.get('width'),
                    'height': img.get('height'),
                    'annotations': image_annotations.get(img['id'], [])
                })
        
        return images_data, {'classes': list(classes.values())}
    
    def parse_yolo(self, extract_path: str) -> Tuple[List[Dict], Dict]:
        """Parse YOLO format"""
        # Find data.yaml
        yaml_files = list(Path(extract_path).rglob("*.yaml")) + list(Path(extract_path).rglob("*.yml"))
        if not yaml_files:
            raise ValueError("No YAML config found")
        
        with open(yaml_files[0], 'r') as f:
            config = yaml.safe_load(f)
        
        classes = config.get('names', [])
        
        # Find images
        images_data = []
        for img_path in Path(extract_path).rglob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                # Find corresponding .txt file
                txt_path = img_path.with_suffix('.txt')
                
                annotations = []
                if txt_path.exists():
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    
                    with open(txt_path, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = int(parts[0])
                                x_center = float(parts[1]) * img_width
                                y_center = float(parts[2]) * img_height
                                width = float(parts[3]) * img_width
                                height = float(parts[4]) * img_height
                                
                                annotations.append({
                                    'class_name': classes[class_id] if class_id < len(classes) else f'class_{class_id}',
                                    'bbox': {
                                        'x': x_center - width / 2,
                                        'y': y_center - height / 2,
                                        'width': width,
                                        'height': height
                                    }
                                })
                else:
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                
                images_data.append({
                    'filename': img_path.name,
                    'path': str(img_path),
                    'width': img_width,
                    'height': img_height,
                    'annotations': annotations
                })
        
        return images_data, {'classes': classes}
    
    def parse_voc(self, extract_path: str) -> Tuple[List[Dict], Dict]:
        """Parse Pascal VOC format"""
        images_data = []
        all_classes = set()
        
        for xml_path in Path(extract_path).rglob("*.xml"):
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            filename = root.find('filename').text
            img_path = self._find_image_file(extract_path, filename)
            
            if not img_path:
                continue
            
            size = root.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)
            
            annotations = []
            for obj in root.findall('object'):
                class_name = obj.find('name').text
                all_classes.add(class_name)
                
                bbox = obj.find('bndbox')
                xmin = float(bbox.find('xmin').text)
                ymin = float(bbox.find('ymin').text)
                xmax = float(bbox.find('xmax').text)
                ymax = float(bbox.find('ymax').text)
                
                annotations.append({
                    'class_name': class_name,
                    'bbox': {
                        'x': xmin,
                        'y': ymin,
                        'width': xmax - xmin,
                        'height': ymax - ymin
                    }
                })
            
            images_data.append({
                'filename': filename,
                'path': img_path,
                'width': width,
                'height': height,
                'annotations': annotations
            })
        
        return images_data, {'classes': list(all_classes)}
    
    def parse_simple(self, extract_path: str) -> Tuple[List[Dict], Dict]:
        """Parse simple image folder (no annotations)"""
        images_data = []
        
        for img_path in Path(extract_path).rglob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                img = Image.open(img_path)
                width, height = img.size
                
                images_data.append({
                    'filename': img_path.name,
                    'path': str(img_path),
                    'width': width,
                    'height': height,
                    'annotations': []
                })
        
        return images_data, {'classes': []}
    
    def _find_image_file(self, base_path: str, filename: str) -> str:
        """Find image file in directory tree"""
        for img_path in Path(base_path).rglob(filename):
            return str(img_path)
        return None
    
    def import_dataset(self, zip_path: str, project_id: str) -> Dict:
        """Main import function"""
        # Extract
        extract_path = self.extract_zip(zip_path, project_id)
        
        # Detect format
        dataset_format = self.detect_format(extract_path)
        
        # Parse based on format
        if dataset_format == "coco":
            images_data, metadata = self.parse_coco(extract_path)
        elif dataset_format == "yolo":
            images_data, metadata = self.parse_yolo(extract_path)
        elif dataset_format == "voc":
            images_data, metadata = self.parse_voc(extract_path)
        else:  # simple
            images_data, metadata = self.parse_simple(extract_path)
        
        return {
            'format': dataset_format,
            'images': images_data,
            'metadata': metadata,
            'total_images': len(images_data),
            'annotated_images': len([img for img in images_data if img['annotations']])
        }
    
    def cleanup(self, project_id: str):
        """Clean up temporary files"""
        extract_path = os.path.join(self.temp_dir, project_id)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
