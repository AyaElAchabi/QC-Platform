#!/usr/bin/env python3
"""
Test de l'API MLOps
"""
import requests
import json

API_URL = "http://localhost:8000"

print("=== Test de l'API MLOps ===\n")

# 1. Test de connexion
print("1. Test de connexion...")
login_data = {
    "email": "admin@mlops.com",
    "password": "admin123"
}

try:
    response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"   ✓ Connexion réussie")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"   ✗ Erreur: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Erreur de connexion: {e}")
    exit(1)

print("\n" + "="*60 + "\n")

# 2. Test de récupération des modèles
print("2. Récupération des modèles...")
headers = {
    "Authorization": f"Bearer {token}"
}

try:
    response = requests.get(f"{API_URL}/models", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        models = response.json()
        print(f"   ✓ {len(models)} modèle(s) trouvé(s)")

        for model in models:
            print(f"\n   📦 Modèle: {model['name']}")
            print(f"      ID: {model['id']}")
            print(f"      Version: {model['version']}")
            print(f"      Stage: {model['stage']}")
            print(f"      Actif: {model['is_active']}")
            print(f"      Architecture: {model['architecture']}")
            print(f"      Storage: {model['storage_path']}")
            if model.get('metrics'):
                metrics = model['metrics']
                if isinstance(metrics, dict):
                    print(f"      Métriques:")
                    if 'map50_95' in metrics:
                        print(f"        - mAP50-95: {metrics['map50_95']:.4f}")
                    if 'map50' in metrics:
                        print(f"        - mAP50: {metrics['map50']:.4f}")
    else:
        print(f"   ✗ Erreur: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    exit(1)

print("\n" + "="*60 + "\n")

# 3. Test d'inférence avec une image de test
print("3. Test d'inférence...")

# Vérifier si une image de test existe
import os
test_images = ["bus.jpg", "zidane.jpg"]
test_image = None

for img in test_images:
    if os.path.exists(img):
        test_image = img
        break

if not test_image:
    print("   ⚠️  Aucune image de test trouvée (bus.jpg ou zidane.jpg)")
    print("   Veuillez ajouter une image pour tester l'inférence")
else:
    if models:
        model_id = models[0]['id']
        print(f"   Utilisation du modèle: {models[0]['name']}")
        print(f"   Image: {test_image}")

        try:
            with open(test_image, 'rb') as f:
                files = {'image': f}
                data = {
                    'model_id': model_id,
                    'confidence_threshold': '0.25',
                    'enable_xai': 'false'
                }

                response = requests.post(
                    f"{API_URL}/api/inference/predict",
                    headers=headers,
                    files=files,
                    data=data
                )

                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✓ Inférence réussie")
                    print(f"   Détections: {result['num_detections']}")
                    print(f"   Temps: {result['inference_time_ms']:.0f}ms")

                    if result['detections']:
                        print(f"\n   Objets détectés:")
                        for det in result['detections']:
                            print(f"     - {det['class_name']}: {det['confidence']:.2%}")
                else:
                    print(f"   ✗ Erreur: {response.text}")
        except Exception as e:
            print(f"   ✗ Erreur lors de l'inférence: {e}")

print("\n" + "="*60)
print("\n✅ Tests terminés!")
