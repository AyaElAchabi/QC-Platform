import requests
from typing import List, Dict
import json


class LabelStudioService:
    """Service pour intégrer Label Studio"""
    
    def __init__(self, base_url: str = "http://labelstudio:8080", api_token: str = None):
        self.base_url = base_url
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Token {api_token}" if api_token else None,
            "Content-Type": "application/json"
        }
    
    def create_project(self, project_name: str, classes: List[Dict]) -> Dict:
        """Crée un projet Label Studio pour un projet MLOps"""
        
        # Configuration XML pour bounding boxes
        label_config = self._generate_label_config(classes)
        
        data = {
            "title": project_name,
            "label_config": label_config,
            "is_published": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/projects",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def _generate_label_config(self, classes: List[Dict]) -> str:
        """Génère la config XML Label Studio pour les classes"""
        
        if not classes:
            classes = [{"name": "defect", "color": "#ff0000"}]
        
        choices = "\n".join([
            f'    <Choice value="{cls["name"]}" background="{cls["color"]}"/>'
            for cls in classes
        ])
        
        config = f"""<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
{choices}
  </RectangleLabels>
</View>"""
        
        return config
    
    def import_images(self, project_id: int, images: List[Dict]) -> Dict:
        """Import images dans un projet Label Studio"""
        
        tasks = []
        for img in images:
            tasks.append({
                "data": {
                    "image": img["url"]
                },
                "meta": {
                    "image_id": img["id"],
                    "filename": img["filename"]
                }
            })
        
        response = requests.post(
            f"{self.base_url}/api/projects/{project_id}/import",
            headers=self.headers,
            json=tasks
        )
        
        return response.json()
    
    def export_annotations(self, project_id: int, format_type: str = "COCO") -> Dict:
        """Exporte les annotations depuis Label Studio"""
        
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}/export",
            headers=self.headers,
            params={"exportType": format_type}
        )
        
        return response.json()
    
    def get_project_stats(self, project_id: int) -> Dict:
        """Récupère les statistiques d'un projet"""
        
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}",
            headers=self.headers
        )
        
        return response.json()
