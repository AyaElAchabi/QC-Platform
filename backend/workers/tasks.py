from datetime import datetime
import os
import yaml
import shutil
from pathlib import Path
from ultralytics import YOLO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from minio import Minio
from workers.celery_app import celery_app

# Configuration
DATABASE_URL = "postgresql://admin:secret@postgres:5432/mlops_qc"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
BUCKET_NAME = "mlops-images"


@celery_app.task(bind=True)
def train_yolo_model(self, job_id: str):
    """Entraîner un modèle YOLOv8"""
    db = SessionLocal()
    
    try:
        # Récupérer le job
        from models.training_job import TrainingJob
        from models.image import ImageModel
        from models.annotation import Annotation
        
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        # Mettre à jour le statut
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Créer workspace
        workspace = f"/tmp/training/{job_id}"
        os.makedirs(workspace, exist_ok=True)
        
        # Préparer le dataset YOLO
        dataset_dir = os.path.join(workspace, "dataset")
        prepare_yolo_dataset(db, job.project_id, dataset_dir)
        
        # Créer data.yaml
        data_yaml_path = create_data_yaml(db, job.project_id, dataset_dir)
        job.dataset_path = dataset_dir
        db.commit()
        
        # Charger le modèle
        model_map = {
            "yolov8n": "yolov8n.pt",
            "yolov8s": "yolov8s.pt",
            "yolov8m": "yolov8m.pt",
            "yolov8l": "yolov8l.pt",
            "yolov8x": "yolov8x.pt",
        }
        
        model = YOLO(model_map[job.model_name])
        
        # Callback pour progression - utilise on_fit_epoch_end qui est appelé après validation
        def on_fit_epoch_end(trainer):
            """Callback appelé à la fin de chaque epoch (après validation)"""
            try:
                epoch = trainer.epoch
                print(f"[CALLBACK DEBUG] on_fit_epoch_end called for epoch {epoch}")
                
                # Récupérer les métriques du trainer
                metrics_dict = {}
                if hasattr(trainer, 'metrics') and trainer.metrics:
                    print(f"[CALLBACK DEBUG] Trainer has metrics: {trainer.metrics}")
                    metrics_dict = {
                        "loss": float(trainer.loss.item()) if hasattr(trainer, 'loss') else 0,
                        "map50": float(trainer.metrics.get('metrics/mAP50(B)', 0)),
                        "map50_95": float(trainer.metrics.get('metrics/mAP50-95(B)', 0)),
                        "precision": float(trainer.metrics.get('metrics/precision(B)', 0)),
                        "recall": float(trainer.metrics.get('metrics/recall(B)', 0)),
                    }
                
                # Créer une nouvelle session DB pour le callback
                callback_db = SessionLocal()
                try:
                    job_update = callback_db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
                    if job_update:
                        job_update.current_epoch = epoch + 1
                        job_update.progress = (epoch + 1) / job.epochs
                        
                        # Ajouter les métriques à l'historique (array)
                        if metrics_dict:
                            # Récupérer l'historique existant ou créer un nouveau
                            metrics_history = job_update.metrics if isinstance(job_update.metrics, list) else []
                            
                            # Ajouter les nouvelles métriques avec l'epoch
                            metrics_history.append({
                                "epoch": epoch + 1,
                                **metrics_dict
                            })
                            
                            job_update.metrics = metrics_history
                        
                        callback_db.commit()
                        print(f"[CALLBACK] Epoch {epoch + 1}/{job.epochs} - Progress: {job_update.progress:.2%} - Metrics: {metrics_dict}")
                    else:
                        print(f"[CALLBACK ERROR] Job {job_id} not found in database")
                finally:
                    callback_db.close()
            except Exception as e:
                print(f"[CALLBACK ERROR] {e}")
                import traceback
                traceback.print_exc()
        
        # Enregistrer le callback
        print(f"[DEBUG] Registering callback on_fit_epoch_end for job {job_id}")
        model.add_callback("on_fit_epoch_end", on_fit_epoch_end)
        
        # Entraîner
        results = model.train(
            data=data_yaml_path,
            epochs=job.epochs,
            batch=job.batch_size,
            imgsz=job.img_size,
            lr0=job.learning_rate,
            patience=job.patience,
            project=workspace,
            name="training",
            save=True,
            plots=True,
        )
        
        # Sauvegarder le modèle dans MinIO
        best_model = os.path.join(workspace, "training", "weights", "best.pt")
        model_storage_path = f"models/{job.project_id}/{job_id}_best.pt"
        
        with open(best_model, 'rb') as f:
            minio_client.put_object(
                BUCKET_NAME,
                model_storage_path,
                f,
                length=os.path.getsize(best_model)
            )
        
        # Finaliser
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.model_path = model_storage_path
        job.progress = 1.0
        db.commit()
        
        # Nettoyer
        shutil.rmtree(workspace)
        
        return {"status": "success", "job_id": str(job_id)}
    
    except Exception as e:
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        raise e
    
    finally:
        db.close()


def prepare_yolo_dataset(db, project_id: str, output_dir: str):
    """Préparer le dataset au format YOLO"""
    from models.image import ImageModel
    from models.annotation import Annotation
    from models.project import Project
    
    # Créer structure
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "labels", split), exist_ok=True)
    
    # Récupérer toutes les images annotées
    images = db.query(ImageModel).filter(
        ImageModel.project_id == project_id,
        ImageModel.status == "annotated"
    ).all()
    
    # Split: 70% train, 20% val, 10% test
    total = len(images)
    train_size = int(0.7 * total)
    val_size = int(0.2 * total)
    
    # Récupérer les classes
    project = db.query(Project).filter(Project.id == project_id).first()
    classes = [c['name'] for c in (project.classes or [])]
    
    for idx, img in enumerate(images):
        # Déterminer split
        if idx < train_size:
            split = "train"
        elif idx < train_size + val_size:
            split = "val"
        else:
            split = "test"
        
        # Télécharger l'image depuis MinIO
        img_dest = os.path.join(output_dir, "images", split, img.filename)
        minio_client.fget_object(BUCKET_NAME, img.storage_path, img_dest)
        
        # Créer le fichier label
        annotations = db.query(Annotation).filter(Annotation.image_id == img.id).all()
        
        label_file = os.path.join(
            output_dir, "labels", split, 
            Path(img.filename).stem + ".txt"
        )
        
        with open(label_file, 'w') as f:
            for ann in annotations:
                # Trouver l'index de la classe
                class_id = classes.index(ann.class_name) if ann.class_name in classes else 0
                
                # Convertir bbox en format YOLO
                bbox = ann.bbox
                x_center = (bbox['x'] + bbox['width'] / 2) / img.width
                y_center = (bbox['y'] + bbox['height'] / 2) / img.height
                width = bbox['width'] / img.width
                height = bbox['height'] / img.height
                
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")


def create_data_yaml(db, project_id: str, dataset_dir: str) -> str:
    """Créer le fichier data.yaml"""
    from models.project import Project
    
    project = db.query(Project).filter(Project.id == project_id).first()
    classes = [c['name'] for c in (project.classes or [])]
    
    data_yaml = {
        'path': dataset_dir,
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': len(classes),
        'names': classes
    }
    
    yaml_path = os.path.join(dataset_dir, 'data.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f)
    
    return yaml_path
