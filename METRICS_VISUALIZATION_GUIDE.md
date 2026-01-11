# Guide de Visualisation des Métriques

## 📊 Vue d'ensemble

Le système MLOps QC Platform affiche maintenant **toutes les métriques métier** de vos modèles YOLOv8 **sans avoir besoin de réentraînement** !

Les métriques sont calculées automatiquement à partir des données d'entraînement existantes.

---

## 🎯 Métriques Disponibles

### 1. **Métriques d'Entraînement** (Déjà stockées)
Ces métriques sont générées pendant l'entraînement et stockées dans la base de données :

- **mAP@50** : Mean Average Precision @ IoU 0.5
- **mAP@50-95** : Mean Average Precision @ IoU 0.5:0.95 (métrique COCO)
- **Précision** : Proportion de détections correctes parmi toutes les détections
- **Rappel** : Proportion d'objets réels détectés
- **Losses** :
  - Box Loss : Erreur de localisation des boîtes
  - Class Loss : Erreur de classification
  - DFL Loss : Distribution Focal Loss

### 2. **Métriques Métier** (Calculées automatiquement)
Ces métriques sont dérivées sans inférence supplémentaire :

#### **TP, FP, FN (True/False Positives/Negatives)**
- **TP (Vrais Positifs)** : Défauts correctement détectés
- **FP (Faux Positifs)** : Fausses alertes (détections incorrectes)
- **FN (Faux Négatifs)** : Défauts manqués (non détectés)

**Formules utilisées :**
```
TP = Précision × Nombre_Prédictions
FP = Nombre_Prédictions - TP
FN = Nombre_Objets_Réels - TP
```

#### **F1-Score**
- Moyenne harmonique de Précision et Rappel
- **Formule :** `F1 = 2 × (Précision × Rappel) / (Précision + Rappel)`
- **Interprétation :**
  - F1 > 0.8 : Excellent
  - F1 > 0.6 : Bon
  - F1 < 0.6 : À améliorer

#### **AUROC (Area Under ROC Curve)**
- Mesure de la capacité du modèle à discriminer
- **Approximation :** Basée sur les mAP
- **Interprétation :**
  - AUROC > 0.9 : Excellent
  - AUROC > 0.8 : Bon
  - AUROC > 0.7 : Acceptable

### 3. **Métriques de Calibration** (Simulées)

#### **ECE (Expected Calibration Error)**
- Mesure l'écart entre confiance prédite et précision réelle
- **Interprétation :**
  - ECE < 5% : Très bien calibré
  - ECE < 10% : Bien calibré
  - ECE < 15% : Calibration acceptable
  - ECE > 15% : Mal calibré

#### **Courbe de Calibration (Reliability Diagram)**
- Graphique confiance vs précision réelle
- **Ligne diagonale** = calibration parfaite
- **Au-dessus** = modèle sous-confiant
- **En-dessous** = modèle sur-confiant

### 4. **Distribution IoU**
- Statistiques sur les IoU des prédictions :
  - Moyenne
  - Écart-type
  - Min/Max

### 5. **Matrice de Confusion par Classe**
- TP, FP, FN pour chaque classe de défaut
- Total global

---

## 🌐 Comment Visualiser

### Option 1 : Interface Web (Recommandé)

1. **Accédez au frontend :** http://localhost:3000

2. **Connectez-vous** avec un compte admin/operator

3. **Naviguez vers un projet :**
   - Allez dans "Projects"
   - Sélectionnez un projet
   - Cliquez sur "Training"
   - Sélectionnez un job **terminé** (status: "completed")

4. **Visualisez les métriques :**
   - **Onglet "Vue d'ensemble"** : Métriques globales (AUROC, ECE, Précision, Rappel, FP/FN)
   - **Onglet "Calibration"** : Courbe de calibration et ECE
   - **Onglet "Matrice de Confusion"** : TP/FP/FN par classe

### Option 2 : Script Python

```bash
python3 /Users/mac/mlops-qc-platform/test_metrics.py
```

Ce script affiche toutes les métriques dans le terminal.

### Option 3 : API REST

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Récupérer les métriques
curl "http://localhost:8000/api/projects/{PROJECT_ID}/training/jobs/{JOB_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.extended_metrics'
```

---

## 🔍 Exemple de Job Terminé

**Job ID :** `86f76964-c761-45f3-87f8-9fbd6338553e`
**Project ID :** `96c4d7ef-445d-448e-afca-3a548d6ebf8f`

**URL directe :**
```
http://localhost:3000/projects/96c4d7ef-445d-448e-afca-3a548d6ebf8f/training/86f76964-c761-45f3-87f8-9fbd6338553e
```

---

## 📈 Graphiques Disponibles

### 1. **Évolution par Epoch**
- Courbe mAP (mAP@50, mAP@50-95)
- Courbe Précision/Rappel
- Courbe des Losses

### 2. **Métriques Avancées** (Onglet "Vue d'ensemble")
- **Cartes de synthèse** : AUROC, ECE, Précision, Rappel
- **Graphique FP/FN** : Visualisation des vrais/faux positifs/négatifs
- **Tableau par classe** : Métriques détaillées pour chaque classe de défaut
- **Distribution IoU** : Statistiques d'intersection

### 3. **Courbe de Calibration** (Onglet "Calibration")
- Diagramme de fiabilité
- Distribution des prédictions par bin de confiance
- ECE avec badge de qualité

### 4. **Matrice de Confusion** (Onglet "Matrice de Confusion")
- Tableau TP/FP/FN par classe
- Codes couleur (vert=TP, rouge=FP, orange=FN)
- Totaux globaux

---

## ⚠️ Notes Importantes

### Données Réelles vs Simulées

| Métrique | Source | Note |
|----------|--------|------|
| mAP, Precision, Recall | **Réel** | Stockées pendant l'entraînement |
| F1-Score | **Calculé** | Dérivé de Precision/Recall |
| TP, FP, FN (globaux) | **Estimé** | Basé sur Precision/Recall |
| AUROC | **Approximé** | Basé sur mAP |
| ECE & Calibration | **Simulé** | Approximation probabiliste |
| TP/FP/FN par classe | **Simulé** | Variation autour des métriques globales |

### Pour des Métriques Exactes

Pour obtenir des métriques **100% exactes** (notamment ECE, AUROC, TP/FP/FN par classe), il faudrait :

1. **Exécuter l'inférence** sur le dataset de validation
2. **Collecter les scores de confiance** de chaque prédiction
3. **Comparer avec les labels vrais** (ground truth)

**Cela ne nécessite PAS de réentraînement**, juste une passe d'inférence.

---

## 🚀 Prochaines Étapes

### Implémentation Future : Métriques Exactes

Pour des métriques de production exactes, implémenter :

```python
# backend/services/metrics/inference_metrics.py
def calculate_exact_metrics_from_validation(
    model_path: str,
    validation_dataset_path: str
) -> Dict:
    """
    Exécute l'inférence sur le dataset de validation
    et calcule les métriques exactes.
    """
    # 1. Charger le modèle
    model = YOLO(model_path)

    # 2. Exécuter l'inférence
    results = model.val(data=validation_dataset_path)

    # 3. Collecter scores de confiance et prédictions
    confidences = []
    predictions = []
    ground_truths = []

    # 4. Calculer métriques exactes
    # - ECE réel
    # - AUROC réel
    # - TP/FP/FN exacts par classe
    # - Matrice de confusion complète

    return metrics
```

---

## 📞 Support

Pour toute question ou problème :

1. Vérifiez que le backend est démarré : `docker ps | grep mlops_backend`
2. Vérifiez que le frontend tourne : `ps aux | grep "next dev"`
3. Consultez les logs : `docker logs mlops_backend --tail 50`

---

## ✅ Checklist de Vérification

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Job d'entraînement complété (status="completed")
- [ ] Navigateur ouvert sur `http://localhost:3000`
- [ ] Connecté avec un compte admin/operator
- [ ] Accès à la page du training job
- [ ] Métriques visibles dans les 3 onglets

---

**🎉 Profitez de vos métriques de qualité visuelle !**
