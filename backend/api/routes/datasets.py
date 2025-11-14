from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from pathlib import Path

from api.dependencies import get_db, get_current_user
from models.user import User
from services.dataset import DatasetImporter

router = APIRouter()


@router.post("/api/projects/{project_id}/upload-dataset")
async def upload_dataset(
    project_id: str,
    file: UploadFile = File(...),
    import_annotations: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload et analyse un dataset ZIP"""
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    # Sauvegarder le ZIP temporairement
    temp_zip = f"/tmp/{file.filename}"
    with open(temp_zip, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Analyser le dataset
        importer = DatasetImporter()
        analysis = importer.analyze_dataset(temp_zip)
        
        return {
            "status": "analyzed",
            "format": analysis['format'],
            "total_images": analysis['total_images'],
            "has_annotations": analysis['has_annotations'],
            "annotated_images": analysis.get('annotated_images', 0),
            "classes": analysis['classes'],
            "extract_path": analysis['extract_path'],
            "message": f"Dataset {analysis['format'].upper()} détecté avec {analysis['total_images']} images"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing dataset: {str(e)}")
    
    finally:
        if os.path.exists(temp_zip):
            os.remove(temp_zip)


@router.post("/api/projects/{project_id}/import-dataset")
async def import_dataset(
    project_id: str,
    extract_path: str = Form(...),
    import_annotations: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Importe réellement le dataset dans le projet"""
    
    # TODO: Implémenter l'import réel avec MinIO et DB
    # 1. Copier les images vers MinIO
    # 2. Créer les entrées en base
    # 3. Si import_annotations, créer aussi les annotations
    
    return {
        "status": "success",
        "message": "Import en cours... (à implémenter)"
    }
