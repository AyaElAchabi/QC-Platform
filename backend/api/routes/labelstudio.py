from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_user
from models.user import User
from models.project import Project
from services.labelstudio import LabelStudioService

router = APIRouter()


@router.post("/api/projects/{project_id}/setup-labelstudio")
async def setup_labelstudio(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Configure Label Studio pour un projet"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Vérifier si déjà configuré
    if project.labelstudio_project_id:
        return {
            "status": "already_configured",
            "labelstudio_url": f"http://localhost:8080/projects/{project.labelstudio_project_id}/",
            "project_id": project.labelstudio_project_id
        }
    
    # Créer le projet dans Label Studio
    ls = LabelStudioService()
    try:
        ls_project = ls.create_project(
            project_name=project.name,
            classes=project.classes or []
        )
        
        # Sauvegarder l'ID Label Studio dans le projet
        project.labelstudio_project_id = str(ls_project["id"])
        db.commit()
        
        return {
            "status": "success",
            "labelstudio_url": f"http://localhost:8080/projects/{ls_project['id']}/",
            "project_id": ls_project["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Label Studio project: {str(e)}")


@router.get("/api/projects/{project_id}/labelstudio-url")
async def get_labelstudio_url(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupère l'URL Label Studio pour un projet"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.labelstudio_project_id:
        raise HTTPException(status_code=404, detail="Label Studio not configured for this project")
    
    return {
        "url": f"http://localhost:8080/projects/{project.labelstudio_project_id}/"
    }


@router.post("/api/projects/{project_id}/sync-annotations")
async def sync_annotations(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Synchronise les annotations depuis Label Studio vers MLOps DB"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.labelstudio_project_id:
        raise HTTPException(status_code=404, detail="Label Studio not configured")
    
    # TODO: Implémenter la synchronisation
    # 1. Récupérer les annotations depuis Label Studio
    # 2. Convertir au format MLOps
    # 3. Sauvegarder en base de données
    
    return {
        "status": "success",
        "message": "Annotations synchronized (to be implemented)"
    }
