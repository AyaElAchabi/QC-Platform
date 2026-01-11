#!/usr/bin/env python3
"""
Script pour créer une entrée Model depuis un TrainingJob terminé
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

# Configuration
DATABASE_URL = "postgresql://admin:secret@postgres:5432/mlops_qc"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_model_from_training_job(job_id: str):
    """Créer un modèle depuis un training job"""
    from models.training_job import TrainingJob
    from models.model import Model, ModelStage
    
    db = SessionLocal()
    try:
        # Récupérer le job
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if not job:
            print(f"❌ Training job {job_id} not found")
            return False
        
        if job.status != "completed":
            print(f"❌ Training job {job_id} is not completed (status: {job.status})")
            return False
        
        if not job.model_path:
            print(f"❌ Training job {job_id} has no model_path")
            return False
        
        # Vérifier si un modèle existe déjà pour ce job
        existing_model = db.query(Model).filter(Model.training_job_id == job.id).first()
        if existing_model:
            print(f"✅ Model already exists: {existing_model.id}")
            print(f"   Name: {existing_model.name}")
            print(f"   Version: {existing_model.version}")
            return True
        
        # Récupérer les métriques finales
        final_metrics = job.metrics[-1] if job.metrics and len(job.metrics) > 0 else {}
        
        # Créer le modèle
        model_entry = Model(
            training_job_id=job.id,
            project_id=job.project_id,
            name=f"{job.model_name}_trained",
            version=f"v1.0_{job.completed_at.strftime('%Y%m%d_%H%M%S') if job.completed_at else datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            task_type="object_detection",
            architecture=job.model_name,
            storage_path=job.model_path,
            metrics=final_metrics,
            hyperparameters={
                "epochs": job.epochs,
                "batch_size": job.batch_size,
                "img_size": job.img_size,
                "learning_rate": job.learning_rate,
                "patience": job.patience
            },
            stage=ModelStage.STAGING,
            is_active=True
            # created_by=job.created_by  # Not available in current schema
        )
        
        db.add(model_entry)
        db.commit()
        db.refresh(model_entry)
        
        print(f"✅ Model created successfully!")
        print(f"   Model ID: {model_entry.id}")
        print(f"   Name: {model_entry.name}")
        print(f"   Version: {model_entry.version}")
        print(f"   Architecture: {model_entry.architecture}")
        print(f"   Storage Path: {model_entry.storage_path}")
        print(f"   Final Metrics: {final_metrics}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_model_from_job.py <training_job_id>")
        print("Example: python create_model_from_job.py 86f76964-c761-45f3-87f8-9fbd6338553e")
        sys.exit(1)
    
    job_id = sys.argv[1]
    success = create_model_from_training_job(job_id)
    sys.exit(0 if success else 1)
