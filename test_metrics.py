#!/usr/bin/env python3
"""Script de test pour visualiser les métriques."""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
PROJECT_ID = "96c4d7ef-445d-448e-afca-3a548d6ebf8f"
JOB_ID = "86f76964-c761-45f3-87f8-9fbd6338553e"

# 1. Login
print("🔐 Connexion...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "admin@test.com", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"❌ Erreur de connexion: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("✅ Connecté!")

# 2. Récupérer les métriques du job
print(f"\n📊 Récupération des métriques du job {JOB_ID[:8]}...")
job_response = requests.get(
    f"{BASE_URL}/api/projects/{PROJECT_ID}/training/jobs/{JOB_ID}",
    headers=headers
)

if job_response.status_code != 200:
    print(f"❌ Erreur: {job_response.status_code}")
    print(job_response.text)
    exit(1)

job_data = job_response.json()

print("✅ Données récupérées!\n")

# 3. Afficher les métriques de base
print("=" * 80)
print("MÉTRIQUES D'ENTRAÎNEMENT")
print("=" * 80)

if job_data.get("metrics"):
    last_epoch = job_data["metrics"][-1]
    print(f"\n📈 Epoch {last_epoch.get('epoch', 'N/A')} (final):")
    print(f"  • mAP@50:      {last_epoch.get('map50', 0) * 100:.1f}%")
    print(f"  • mAP@50-95:   {last_epoch.get('map50_95', 0) * 100:.1f}%")
    print(f"  • Précision:   {last_epoch.get('precision', 0) * 100:.1f}%")
    print(f"  • Rappel:      {last_epoch.get('recall', 0) * 100:.1f}%")
    print(f"  • Box Loss:    {last_epoch.get('box_loss', 0):.4f}")
    print(f"  • Class Loss:  {last_epoch.get('cls_loss', 0):.4f}")

# 4. Afficher les métriques étendues
if job_data.get("extended_metrics"):
    ext = job_data["extended_metrics"]

    print("\n" + "=" * 80)
    print("MÉTRIQUES ÉTENDUES (CALCULÉES)")
    print("=" * 80)

    # Business Metrics
    if ext.get("business_metrics"):
        bm = ext["business_metrics"]
        print("\n🎯 Métriques Métier:")
        print(f"  • Vrais Positifs (TP):  {bm['global']['total_tp']}")
        print(f"  • Faux Positifs (FP):   {bm['global']['total_fp']}")
        print(f"  • Faux Négatifs (FN):   {bm['global']['total_fn']}")
        print(f"  • F1-Score:             {bm['global']['f1'] * 100:.1f}%")

    # AUROC
    if ext.get("auroc") is not None:
        print(f"\n📊 AUROC: {ext['auroc'] * 100:.1f}%")

    # Calibration
    if ext.get("calibration"):
        cal = ext["calibration"]
        print(f"\n🎯 Calibration:")
        print(f"  • ECE (Expected Calibration Error): {cal['ece'] * 100:.2f}%")
        if cal['ece'] <= 0.05:
            print(f"    → Excellent (très bien calibré)")
        elif cal['ece'] <= 0.10:
            print(f"    → Bon (bien calibré)")
        elif cal['ece'] <= 0.15:
            print(f"    → Modéré (calibration acceptable)")
        else:
            print(f"    → Faible (mal calibré)")

    # IoU Distribution
    if ext.get("iou_distribution"):
        iou = ext["iou_distribution"]
        print(f"\n📏 Distribution IoU:")
        print(f"  • Moyenne:     {iou['mean'] * 100:.1f}%")
        print(f"  • Écart-type:  {iou['std'] * 100:.1f}%")
        print(f"  • Min:         {iou['min'] * 100:.1f}%")
        print(f"  • Max:         {iou['max'] * 100:.1f}%")

    # Confusion Matrix
    if ext.get("confusion_matrix") and job_data.get("class_names"):
        cm = ext["confusion_matrix"]
        classes = job_data["class_names"]

        print(f"\n🔢 Matrice de Confusion (IoU ≥ {cm['iou_threshold'] * 100:.0f}%):")
        print(f"\n  {'Classe':<20} {'TP':>8} {'FP':>8} {'FN':>8}")
        print(f"  {'-' * 20} {'-' * 8} {'-' * 8} {'-' * 8}")

        for class_name in classes:
            tp = cm['tp_per_class'].get(class_name, 0)
            fp = cm['fp_per_class'].get(class_name, 0)
            fn = cm['fn_per_class'].get(class_name, 0)
            print(f"  {class_name:<20} {tp:>8} {fp:>8} {fn:>8}")

        print(f"  {'-' * 20} {'-' * 8} {'-' * 8} {'-' * 8}")
        print(f"  {'TOTAL':<20} {cm['total_tp']:>8} {cm['total_fp']:>8} {cm['total_fn']:>8}")

print("\n" + "=" * 80)
print("✅ MÉTRIQUES AFFICHÉES AVEC SUCCÈS!")
print("=" * 80)

# 5. Sauvegarder en JSON pour inspection
with open("/tmp/metrics_output.json", "w") as f:
    json.dump(job_data, f, indent=2)

print(f"\n💾 Données complètes sauvegardées dans: /tmp/metrics_output.json")
print(f"\n🌐 Ouvrez le frontend pour voir les visualisations graphiques:")
print(f"   http://localhost:3000/projects/{PROJECT_ID}/training/{JOB_ID}")
