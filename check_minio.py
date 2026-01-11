#!/usr/bin/env python3
"""
Script pour vérifier les fichiers dans MinIO
"""
from minio import Minio
from minio.error import S3Error

# Configuration MinIO
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

print("=== Vérification MinIO ===\n")

# Lister tous les buckets
print("Buckets disponibles:")
try:
    buckets = minio_client.list_buckets()
    for bucket in buckets:
        print(f"  - {bucket.name} (créé le {bucket.creation_date})")
except S3Error as e:
    print(f"  Erreur: {e}")

print("\n" + "="*50 + "\n")

# Vérifier le bucket mlops-models
bucket_name = "mlops-models"
print(f"Contenu du bucket '{bucket_name}':")

try:
    # Vérifier si le bucket existe
    if not minio_client.bucket_exists(bucket_name):
        print(f"  ⚠️  Le bucket '{bucket_name}' n'existe pas!")
        print(f"  📁 Création du bucket '{bucket_name}'...")
        minio_client.make_bucket(bucket_name)
        print(f"  ✓ Bucket créé avec succès")
    else:
        print(f"  ✓ Le bucket existe")

    # Lister les objets
    objects = minio_client.list_objects(bucket_name, recursive=True)
    files_found = False

    for obj in objects:
        files_found = True
        size_mb = obj.size / (1024 * 1024)
        print(f"  📄 {obj.object_name} ({size_mb:.2f} MB)")

    if not files_found:
        print("  ℹ️  Le bucket est vide")

except S3Error as e:
    print(f"  Erreur: {e}")

print("\n" + "="*50 + "\n")

# Vérifier les chemins de modèles spécifiques
model_paths = [
    "models/96c4d7ef-445d-448e-afca-3a548d6ebf8f/86f76964-c761-45f3-87f8-9fbd6338553e_best.pt",
    "models/96c4d7ef-445d-448e-afca-3a548d6ebf8f/d41364eb-72bd-4eec-8122-2bfadee4587c_best.pt",
    "models/96c4d7ef-445d-448e-afca-3a548d6ebf8f/6c3cb690-996f-4acc-807d-af5b59a6ddb7_best.pt"
]

print("Vérification des modèles entraînés:")
for path in model_paths:
    try:
        stat = minio_client.stat_object(bucket_name, path)
        size_mb = stat.size / (1024 * 1024)
        print(f"  ✓ {path}")
        print(f"    Taille: {size_mb:.2f} MB")
        print(f"    Modifié: {stat.last_modified}")
    except S3Error as e:
        if e.code == "NoSuchKey":
            print(f"  ✗ {path} - FICHIER MANQUANT")
        else:
            print(f"  ✗ {path} - Erreur: {e}")

print("\n" + "="*50)
