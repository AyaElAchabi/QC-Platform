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
from services.metrics import metrics_service

# Configuration
DATABASE_URL = "postgresql://admin:secret@postgres:5432/mlops_qc"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
BUCKET_NAME = "mlops-images"  # Pour les images du dataset
MODELS_BUCKET = "mlops-models"  # Pour les modèles entraînés


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
                        # Métriques de performance
                        "map50": float(trainer.metrics.get('metrics/mAP50(B)', 0)),
                        "map50_95": float(trainer.metrics.get('metrics/mAP50-95(B)', 0)),
                        "precision": float(trainer.metrics.get('metrics/precision(B)', 0)),
                        "recall": float(trainer.metrics.get('metrics/recall(B)', 0)),
                        # Losses (pour le graphique Losses)
                        "box_loss": float(trainer.metrics.get('val/box_loss', 0)),
                        "cls_loss": float(trainer.metrics.get('val/cls_loss', 0)),
                        "dfl_loss": float(trainer.metrics.get('val/dfl_loss', 0)),
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
                            
                            # IMPORTANT: Forcer SQLAlchemy à détecter le changement dans le JSON
                            from sqlalchemy.orm.attributes import flag_modified
                            job_update.metrics = metrics_history
                            flag_modified(job_update, "metrics")
                        
                        callback_db.commit()
                        print(f"[CALLBACK] Epoch {epoch + 1}/{job.epochs} - Progress: {job_update.progress:.2%} - Metrics saved: {len(metrics_history)} epochs")
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
        
        # S'assurer que le bucket mlops-models existe
        try:
            if not minio_client.bucket_exists(MODELS_BUCKET):
                minio_client.make_bucket(MODELS_BUCKET)
                print(f"✅ Created MinIO bucket: {MODELS_BUCKET}")
        except Exception as e:
            print(f"⚠️ Bucket check/creation warning: {e}")
        
        # Upload du modèle dans MinIO
        with open(best_model, 'rb') as f:
            file_size = os.path.getsize(best_model)
            minio_client.put_object(
                MODELS_BUCKET,
                model_storage_path,
                f,
                length=file_size
            )
        
        print(f"✅ Model uploaded to MinIO: {MODELS_BUCKET}/{model_storage_path} ({file_size} bytes)")
        
        # ============ COMPUTE EXTENDED METRICS ============
        print("[METRICS] Computing extended metrics on validation set...")
        extended_metrics = None
        class_names = []
        
        try:
            # Récupérer les classes du projet
            from models.project import Project
            project = db.query(Project).filter(Project.id == job.project_id).first()
            class_names = [c['name'] for c in (project.classes or [])]
            
            # Charger le modèle entraîné
            trained_model = YOLO(best_model)
            
            # Effectuer la validation sur le dataset de validation
            val_images_dir = os.path.join(dataset_dir, "images", "val")
            val_labels_dir = os.path.join(dataset_dir, "labels", "val")
            
            predictions = []
            ground_truths = []
            
            # Parcourir les images de validation
            if os.path.exists(val_images_dir):
                import glob
                from PIL import Image as PILImage
                
                val_images = glob.glob(os.path.join(val_images_dir, "*"))
                print(f"[METRICS] Processing {len(val_images)} validation images...")
                
                for img_path in val_images:
                    try:
                        # Prédiction sur l'image
                        img = PILImage.open(img_path)
                        img_width, img_height = img.size
                        
                        results = trained_model.predict(img_path, conf=0.25, verbose=False)
                        
                        # Collecter les prédictions
                        if results and len(results) > 0:
                            result = results[0]
                            if result.boxes is not None:
                                for box in result.boxes:
                                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                                    class_id = int(box.cls[0].cpu().numpy())
                                    confidence = float(box.conf[0].cpu().numpy())
                                    
                                    predictions.append({
                                        "bbox": [x1, y1, x2, y2],
                                        "class_name": class_names[class_id] if class_id < len(class_names) else f"class_{class_id}",
                                        "confidence": confidence
                                    })
                        
                        # Charger les ground truths depuis les fichiers labels
                        label_file = os.path.join(
                            val_labels_dir,
                            Path(img_path).stem + ".txt"
                        )
                        
                        if os.path.exists(label_file):
                            with open(label_file, 'r') as f:
                                for line in f:
                                    parts = line.strip().split()
                                    if len(parts) >= 5:
                                        class_id = int(parts[0])
                                        x_center = float(parts[1]) * img_width
                                        y_center = float(parts[2]) * img_height
                                        width = float(parts[3]) * img_width
                                        height = float(parts[4]) * img_height
                                        
                                        x1 = x_center - width / 2
                                        y1 = y_center - height / 2
                                        x2 = x_center + width / 2
                                        y2 = y_center + height / 2
                                        
                                        ground_truths.append({
                                            "bbox": [x1, y1, x2, y2],
                                            "class_name": class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
                                        })
                    except Exception as img_err:
                        print(f"[METRICS] Warning processing image {img_path}: {img_err}")
                        continue
                
                print(f"[METRICS] Collected {len(predictions)} predictions, {len(ground_truths)} ground truths")
                
                # Calculer les métriques étendues
                if predictions or ground_truths:
                    extended_metrics = metrics_service.compute_all_metrics(
                        predictions=predictions,
                        ground_truths=ground_truths,
                        class_names=class_names,
                        iou_threshold=0.5
                    )
                    print(f"[METRICS] Extended metrics computed successfully!")
                    print(f"[METRICS] AUROC: {extended_metrics.get('auroc', 'N/A')}, ECE: {extended_metrics.get('calibration', {}).get('ece', 'N/A')}")
                else:
                    print("[METRICS] No predictions or ground truths to compute metrics")
        except Exception as metrics_err:
            print(f"[METRICS] Error computing extended metrics: {metrics_err}")
            import traceback
            traceback.print_exc()
        # ============ END EXTENDED METRICS ============
        
        # Finaliser le job
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.model_path = model_storage_path
        job.progress = 1.0
        
        # Créer une entrée dans la table models
        from models.model import Model, ModelStage
        
        # Récupérer les métriques finales (dernière epoch)
        final_metrics = job.metrics[-1] if job.metrics and len(job.metrics) > 0 else {}
        
        # Ajouter les métriques étendues aux métriques finales
        if extended_metrics:
            final_metrics["extended_metrics"] = extended_metrics
        
        # Stocker les class_names dans le job pour le frontend
        if class_names:
            final_metrics["class_names"] = class_names
        
        # Mettre à jour le job avec les métriques étendues
        from sqlalchemy.orm.attributes import flag_modified
        if job.metrics and len(job.metrics) > 0:
            job.metrics[-1] = final_metrics
            flag_modified(job, "metrics")
        
        # Créer le modèle
        model_entry = Model(
            training_job_id=job.id,
            project_id=job.project_id,
            name=f"{job.model_name}_trained",
            version=f"v1.0_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            task_type="object_detection",
            architecture=job.model_name,
            storage_path=model_storage_path,
            metrics=final_metrics,
            hyperparameters={
                "epochs": job.epochs,
                "batch_size": job.batch_size,
                "img_size": job.img_size,
                "learning_rate": job.learning_rate,
                "patience": job.patience
            },
            stage=ModelStage.STAGING,
            is_active=True,
            created_by=job.created_by
        )
        
        db.add(model_entry)
        db.commit()
        
        print(f"[SUCCESS] Model saved to database: {model_entry.id}")
        if extended_metrics:
            print(f"[SUCCESS] Extended metrics included in model")
        
        # Nettoyer
        shutil.rmtree(workspace)
        
        return {"status": "success", "job_id": str(job_id), "has_extended_metrics": extended_metrics is not None}
    
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
