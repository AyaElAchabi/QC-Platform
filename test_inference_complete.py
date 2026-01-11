#!/usr/bin/env python3
"""
Test complet de l'inférence avec une image
"""
import requests
import os

API_URL = "http://localhost:8000"

print("="*60)
print("🧪 TEST COMPLET D'INFÉRENCE")
print("="*60 + "\n")

# 1. Connexion
print("1. 🔐 Authentification...")
login_data = {
    "email": "admin@test.com",
    "password": "Admin@2024"
}

try:
    response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("   ✅ Connexion réussie\n")
    else:
        print(f"   ❌ Erreur: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# 2. Récupérer les modèles
print("2. 📦 Récupération des modèles...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(f"{API_URL}/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        if not models:
            print("   ❌ Aucun modèle disponible")
            exit(1)

        model = models[0]
        print(f"   ✅ Modèle trouvé: {model['name']}")
        print(f"      - Version: {model['version']}")
        print(f"      - Architecture: {model['architecture']}")
        print(f"      - mAP50-95: {model['metrics']['map50_95']:.2%}")
        print(f"      - Stage: {model['stage']}")
        print()
    else:
        print(f"   ❌ Erreur: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# 3. Test d'inférence
print("3. 🖼️  Test d'inférence...")

# Trouver une image de test
test_images = ["zidane.jpg", "bus.jpg"]  # Préférer zidane.jpg en premier
test_image = None

for img in test_images:
    if os.path.exists(img):
        # Vérifier que c'est bien une image
        import subprocess
        result = subprocess.run(['file', img], capture_output=True, text=True)
        if 'image' in result.stdout.lower() or 'jpeg' in result.stdout.lower():
            test_image = img
            break

if not test_image:
    print("   ⚠️  Aucune image de test trouvée")
    print("   💡 Téléchargez une image et placez-la dans le dossier actuel")
    print("   💡 Vous pouvez utiliser: bus.jpg, zidane.jpg ou n'importe quelle image")
    exit(0)

print(f"   📸 Image: {test_image}")

try:
    with open(test_image, 'rb') as f:
        files = {'image': f}
        data = {
            'model_id': model['id'],
            'confidence_threshold': '0.25',
            'enable_xai': 'false'
        }

        print(f"   ⏳ Détection en cours...")
        response = requests.post(
            f"{API_URL}/api/inference/predict",
            headers=headers,
            files=files,
            data=data
        )

        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Inférence réussie!")
            print(f"\n   📊 Résultats:")
            print(f"      - Détections: {result['num_detections']}")
            print(f"      - Temps: {result['inference_time_ms']:.0f}ms")
            print(f"      - Seuil: {result['confidence_threshold']:.0%}")

            if result['detections']:
                print(f"\n   🎯 Objets détectés:")
                for i, det in enumerate(result['detections'], 1):
                    print(f"      {i}. {det['class_name']}")
                    print(f"         - Confiance: {det['confidence']:.1%}")
                    print(f"         - Position: {det['bbox']}")
            else:
                print(f"\n   ℹ️  Aucun objet détecté (essayez de réduire le seuil de confiance)")

            print(f"\n   💾 ID Prédiction: {result['prediction_id']}")

        else:
            error = response.json()
            print(f"   ❌ Erreur: {error.get('detail', 'Erreur inconnue')}")
            exit(1)

except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ TOUS LES TESTS RÉUSSIS!")
print("="*60)
print("\n💡 Vous pouvez maintenant utiliser l'interface web:")
print("   🌐 http://localhost:3000/inference/detect")
print(f"   👤 Email: admin@test.com")
print(f"   🔑 Password: Admin@2024")
print()
