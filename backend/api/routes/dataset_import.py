from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
import hashlib
from datetime import datetime
from minio import Minio
import io

from api.dependencies import get_db, get_current_user
from models.user import User
from models.project import Project
from models.image import ImageModel
from models.annotation import Annotation
from services.dataset_import import DatasetImporter

router = APIRouter()

minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
BUCKET_NAME = "mlops-images"


@router.post("/api/projects/{project_id}/import-dataset")
async def import_dataset(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files supported")
    
    try:
        temp_zip = f"/tmp/{uuid.uuid4()}.zip"
        contents = await file.read()
        with open(temp_zip, "wb") as f:
            f.write(contents)
        
        importer = DatasetImporter()
        result = importer.import_dataset(temp_zip, project_id)
        
        imported_count = 0
        skipped_count = 0
        annotations_count = 0
        
        for img_data in result["images"]:
            with open(img_data["path"], "rb") as f:
                img_contents = f.read()
            
            file_hash = hashlib.md5(img_contents).hexdigest()
            
            existing = db.query(ImageModel).filter(
                ImageModel.file_hash == file_hash,
                ImageModel.project_id == project_id
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            image_id = str(uuid.uuid4())
            storage_path = f"projects/{project_id}/images/{image_id}_{img_data['filename']}"
            
            minio_client.put_object(
                BUCKET_NAME,
                storage_path,
                io.BytesIO(img_contents),
                length=len(img_contents),
                content_type="image/jpeg"
            )
            
            new_image = ImageModel(
                id=image_id,
                project_id=project_id,
                filename=img_data["filename"],
                storage_path=storage_path,
                file_hash=file_hash,
                width=img_data["width"],
                height=img_data["height"],
                status="annotated" if img_data["annotations"] else "uploaded",
                created_at=datetime.utcnow(),
            )
            db.add(new_image)
            db.flush()
            
            for ann in img_data["annotations"]:
                annotation = Annotation(
                    id=str(uuid.uuid4()),
                    image_id=image_id,
                    class_name=ann["class_name"],
                    bbox=ann["bbox"],
                    confidence=1.0,
                    created_by=current_user.id,
                    created_at=datetime.utcnow(),
                )
                db.add(annotation)
                annotations_count += 1
            
            imported_count += 1
        
        if result["metadata"]["classes"]:
            existing_classes = [c["name"] for c in (project.classes or [])]
            new_classes = [c for c in result["metadata"]["classes"] if c not in existing_classes]
            
            if new_classes:
                if not project.classes:
                    project.classes = []
                
                for class_name in new_classes:
                    project.classes.append({
                        "name": class_name,
                        "color": f"#{hash(class_name) % 0xFFFFFF:06x}"
                    })
        
        db.commit()
        
        importer.cleanup(project_id)
        os.remove(temp_zip)
        
        return {
            "message": "Dataset imported successfully",
            "format": result["format"],
            "total_images": result["total_images"],
            "imported": imported_count,
            "skipped": skipped_count,
            "annotated": result["annotated_images"],
            "annotations_count": annotations_count,
            "classes": result["metadata"]["classes"]
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")
