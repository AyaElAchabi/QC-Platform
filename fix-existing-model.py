#!/usr/bin/env python3
"""
Script pour uploader manuellement les modèles existants dans MinIO
"""
import os
from minio import Minio
import psycopg2
from datetime import datetime

# Configuration
MINIO_CLIENT = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mlops_qc",
    "user": "admin",
    "password": "secret"
}

MODELS_BUCKET = "mlops-models"

def ensure_bucket():
    """S'assurer que le bucket existe"""
    if not MINIO_CLIENT.bucket_exists(MODELS_BUCKET):
        MINIO_CLIENT.make_bucket(MODELS_BUCKET)
        print(f"✅ Bucket {MODELS_BUCKET} créé")
    else:
        print(f"✅ Bucket {MODELS_BUCKET} existe déjà")

def get_models_from_db():
    """Récupérer tous les modèles de la base"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.id, m.name, m.storage_path, tj.id as job_id
        FROM models m
        LEFT JOIN training_jobs tj ON m.training_job_id = tj.id
        ORDER BY m.created_at DESC
    """)
    
    models = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return models

def check_model_in_minio(storage_path):
    """Vérifier si un modèle existe dans MinIO"""
    try:
        MINIO_CLIENT.stat_object(MODELS_BUCKET, storage_path)
        return True
    except Exception:
        return False

def upload_dummy_model(storage_path):
    """
    Créer et uploader un modèle YOLOv8n de base comme placeholder
    pour permettre le test de l'inférence
    """
    try:
        # Le fichier yolov8n.pt est déjà dans le répertoire courant après le premier téléchargement
        model_file = "yolov8n.pt"
        
        if not os.path.exists(model_file):
            print("📥 Téléchargement de yolov8n.pt...")
            from ultralytics import YOLO
            # Le modèle sera téléchargé automatiquement
            model = YOLO("yolov8n.pt")
            # Utiliser le fichier téléchargé
            model_file = "yolov8n.pt"
        
        # Upload vers MinIO
        with open(model_file, "rb") as f:
            file_size = os.path.getsize(model_file)
            MINIO_CLIENT.put_object(
                MODELS_BUCKET,
                storage_path,
                f,
                length=file_size
            )
        
        print(f"✅ Modèle placeholder uploadé: {storage_path} ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Script de correction des modèles existants")
    print("=" * 60)
    
    # 1. Vérifier/créer le bucket
    ensure_bucket()
    print()
    
    # 2. Lister les modèles dans la base
    print("📋 Modèles dans la base de données:")
    models = get_models_from_db()
    
    if not models:
        print("❌ Aucun modèle trouvé dans la base")
        return
    
    for model_id, name, storage_path, job_id in models:
        print(f"\n🔹 Modèle: {name}")
        print(f"   ID: {model_id}")
        print(f"   Storage Path: {storage_path}")
        print(f"   Job ID: {job_id}")
        
        # Vérifier si le modèle existe dans MinIO
        exists = check_model_in_minio(storage_path)
        if exists:
            print(f"   ✅ Existe dans MinIO")
        else:
            print(f"   ❌ Absent de MinIO")
            
            # Proposer d'uploader un modèle placeholder
            response = input("   Voulez-vous uploader un modèle YOLOv8n de base? (y/n): ")
            if response.lower() == 'y':
                upload_dummy_model(storage_path)
    
    print("\n" + "=" * 60)
    print("✅ Script terminé")
    
    # Afficher les objets dans MinIO
    print("\n📦 Objets dans MinIO:")
    try:
        objects = MINIO_CLIENT.list_objects(MODELS_BUCKET, recursive=True)
        for obj in objects:
            print(f"   - {obj.object_name} ({obj.size} bytes)")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    main()
