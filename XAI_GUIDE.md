# 🧠 Guide XAI (Explainable AI) - MLOps QC Platform

## Vue d'ensemble

Le module XAI (Explainable AI) permet de visualiser et comprendre **pourquoi** votre modèle YOLOv8 prend certaines décisions. Il génère des explications visuelles qui mettent en évidence les zones importantes de l'image pour la détection de défauts.

---

## 🎯 Méthodes XAI Disponibles

### 1. **Grad-CAM** ✅ (Disponible)
**Gradient-weighted Class Activation Mapping**

- **Description** : Visualise les zones de l'image qui ont le plus d'impact sur les prédictions du modèle
- **Avantage** : Rapide, facile à interpréter
- **Utilisation** : Idéal pour comprendre rapidement où le modèle "regarde"
- **Vitesse** : ⚡ Rapide (< 1 seconde)

**Interprétation** :
- 🔴 **Rouge/Jaune** : Zones très importantes (forte activation)
- 🟢 **Vert/Bleu** : Zones moins importantes
- ⚫ **Noir/Bleu foncé** : Zones ignorées

### 2. **Grad-CAM++** ✅ (Disponible)
**Version améliorée de Grad-CAM**

- **Description** : Amélioration de Grad-CAM avec pondération multiple des gradients
- **Avantage** : Plus précis pour les détections multiples dans une même image
- **Utilisation** : Quand plusieurs objets/défauts sont présents
- **Vitesse** : ⚡ Rapide (< 1 seconde)

### 3. **LIME** 🔜 (Bientôt disponible)
**Local Interpretable Model-agnostic Explanations**

- **Description** : Crée des explications locales en perturbant l'image
- **Avantage** : Indépendant du modèle, très interprétable
- **Utilisation** : Pour des explications détaillées région par région
- **Vitesse** : 🟡 Lent (10-30 secondes)

### 4. **Integrated Gradients** 🔜 (Bientôt disponible)
**Attribution des gradients intégrés (Captum)**

- **Description** : Calcule l'attribution de chaque pixel à la prédiction
- **Avantage** : Mathématiquement rigoureux
- **Utilisation** : Pour des analyses scientifiques précises
- **Vitesse** : 🟠 Moyen (5-10 secondes)

### 5. **SHAP** 🔜 (Bientôt disponible)
**SHapley Additive exPlanations**

- **Description** : Basé sur la théorie des jeux pour attribuer l'importance
- **Avantage** : Théoriquement optimal
- **Utilisation** : Pour des rapports scientifiques
- **Vitesse** : 🔴 Très lent (30-60 secondes)

---

## 🚀 Comment Utiliser XAI

### Option 1 : Interface Web (Recommandé)

#### **Étape 1 : Accéder à la page XAI**
```
http://localhost:3000/xai
```

#### **Étape 2 : Charger une image**
- Cliquez sur "Uploader une image" et sélectionnez une image
- OU entrez le chemin d'une image déjà sur le serveur

#### **Étape 3 : Sélectionner les méthodes**
- Cochez les méthodes XAI souhaitées (Grad-CAM, Grad-CAM++)
- Les méthodes marquées "Bientôt" ne sont pas encore disponibles

#### **Étape 4 : Générer les explications**
- Cliquez sur "Générer"
- Attendez quelques secondes
- Les heatmaps s'affichent dans des onglets séparés

#### **Étape 5 : Télécharger les résultats**
- Cliquez sur "Télécharger" pour sauvegarder chaque heatmap

### Option 2 : API REST

#### **Endpoint : POST /api/xai/generate**

**Requête :**
```bash
curl -X POST "http://localhost:8000/api/xai/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.jpg",
    "methods": ["gradcam", "gradcam++"],
    "model_id": "model-uuid-optional"
  }'
```

**Réponse :**
```json
{
  "explanations": {
    "gradcam": {
      "method": "gradcam",
      "heatmap": "data:image/png;base64,iVBOR...",
      "target_layer": "model.22",
      "success": true
    },
    "gradcam++": {
      "method": "gradcam++",
      "heatmap": "data:image/png;base64,iVBOR...",
      "success": true
    }
  },
  "image_path": "/path/to/image.jpg",
  "model_id": "..."
}
```

#### **Endpoint : GET /api/xai/methods**

Liste toutes les méthodes XAI disponibles :
```bash
curl "http://localhost:8000/api/xai/methods" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### **Endpoint : GET /api/predictions/{prediction_id}/xai**

Génère des explications pour une prédiction existante :
```bash
curl "http://localhost:8000/api/predictions/{prediction_id}/xai?methods=gradcam&methods=gradcam++" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Cas d'Usage

### 1. **Validation du Modèle**
**Objectif** : Vérifier que le modèle regarde les bonnes zones

**Procédure** :
1. Sélectionnez des images de test avec des défauts évidents
2. Générez des heatmaps Grad-CAM
3. Vérifiez que les zones rouges correspondent aux défauts réels

**Résultat attendu** : Les heatmaps doivent se concentrer sur les défauts, pas sur le fond

### 2. **Débogage des Faux Positifs**
**Objectif** : Comprendre pourquoi le modèle détecte un défaut qui n'existe pas

**Procédure** :
1. Prenez une image avec un faux positif
2. Générez Grad-CAM++ pour voir la zone activée
3. Analysez ce qui dans cette zone ressemble à un défaut

**Action** : Ajouter des images similaires en négatif au dataset d'entraînement

### 3. **Amélioration du Dataset**
**Objectif** : Identifier les types d'images qui posent problème

**Procédure** :
1. Sélectionnez des images où le modèle échoue
2. Comparez les heatmaps entre bonnes et mauvaises prédictions
3. Identifiez les patterns problématiques

**Action** : Enrichir le dataset avec ces cas difficiles

### 4. **Conformité et Auditabilité**
**Objectif** : Prouver que le modèle prend des décisions basées sur des critères valides

**Procédure** :
1. Générez des explications pour un ensemble de prédictions
2. Créez un rapport avec images originales + heatmaps
3. Documentez que les zones importantes correspondent aux critères métier

**Résultat** : Rapport d'audit pour certification ISO/qualité

### 5. **Communication avec les Opérateurs**
**Objectif** : Former les opérateurs à comprendre le modèle

**Procédure** :
1. Créez une bibliothèque d'exemples avec heatmaps
2. Montrez des cas typiques : défauts clairs, ambigus, difficiles
3. Expliquez comment interpréter les couleurs

**Résultat** : Opérateurs capables de juger la fiabilité des prédictions

---

## 🔬 Interprétation des Résultats

### Grad-CAM / Grad-CAM++

#### **Bonne Prédiction**
```
✅ La heatmap est concentrée sur le défaut
✅ Les zones activées correspondent visuellement au défaut
✅ Le fond est peu ou pas activé (bleu/noir)
```

#### **Prédiction Douteuse**
```
⚠️ La heatmap est dispersée sur plusieurs zones
⚠️ Des zones activées ne contiennent pas de défaut visible
⚠️ L'activation est faible (couleurs ternes)
```

#### **Mauvaise Prédiction**
```
❌ La heatmap active le fond ou des zones sans défaut
❌ Le défaut réel n'est PAS dans une zone rouge/jaune
❌ L'activation est uniforme (pas de focus clair)
```

### Code Couleur Standard

| Couleur | Activation | Interprétation |
|---------|-----------|----------------|
| 🔴 Rouge vif | > 90% | Zone TRÈS importante |
| 🟠 Orange | 70-90% | Zone importante |
| 🟡 Jaune | 50-70% | Zone modérément importante |
| 🟢 Vert | 30-50% | Zone peu importante |
| 🔵 Bleu | 10-30% | Zone très peu importante |
| ⚫ Noir | < 10% | Zone ignorée |

---

## ⚙️ Configuration Technique

### Dépendances Backend

Le service XAI nécessite ces bibliothèques Python :
```bash
pip install pytorch-grad-cam  # Pour Grad-CAM
pip install shap              # Pour SHAP (optionnel)
pip install lime              # Pour LIME (optionnel)
pip install captum            # Pour Integrated Gradients (optionnel)
```

Ces dépendances sont **déjà incluses** dans `requirements.txt`.

### Architecture Backend

```
backend/
├── services/xai/
│   ├── __init__.py
│   └── xai_service.py          # Service principal XAI
├── api/routes/
│   └── xai.py                  # Routes API XAI
└── models/
    └── xai_artifact.py         # Stockage des explications (optionnel)
```

### Architecture Frontend

```
frontend/src/
├── app/(app)/xai/
│   └── page.tsx                # Page XAI
└── components/xai/
    └── XAIVisualization.tsx    # Composant de visualisation
```

---

## 🧪 Tests et Validation

### Test 1 : Génération Grad-CAM

**Commande** :
```bash
# Via API
curl -X POST "http://localhost:8000/api/xai/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_path":"zidane.jpg","methods":["gradcam"]}'
```

**Résultat attendu** :
- Status 200
- `success: true`
- `heatmap` contient une image base64

### Test 2 : Interface Web

**Procédure** :
1. Aller sur http://localhost:3000/xai
2. Uploader `zidane.jpg` ou `bus.jpg` (images de test YOLOv8)
3. Sélectionner Grad-CAM
4. Cliquer sur "Générer"

**Résultat attendu** :
- Heatmap affichée en 1-2 secondes
- Zones rouges sur les personnes/objets détectés
- Possibilité de télécharger l'image

### Test 3 : Comparaison Grad-CAM vs Grad-CAM++

**Procédure** :
1. Charger une image avec plusieurs objets
2. Générer les deux méthodes simultanément
3. Comparer les résultats dans les onglets

**Observation** :
- Grad-CAM++ devrait mieux localiser chaque objet individuel
- Grad-CAM peut avoir des activations plus larges

---

## 📝 Limitations Actuelles

### Méthodes Disponibles
- ✅ **Grad-CAM** : Fonctionnel
- ✅ **Grad-CAM++** : Fonctionnel
- ⏳ **LIME** : Code prêt, à activer
- ⏳ **Integrated Gradients** : Code prêt, à activer
- ⏳ **SHAP** : Code prêt, à activer

### Limitations Techniques

1. **Performance** : Les méthodes lentes (LIME, SHAP) ne sont pas encore optimisées
2. **Modèles** : Optimisé pour YOLOv8, peut ne pas fonctionner avec d'autres architectures
3. **Batch** : Une image à la fois (pas de traitement par lot)
4. **Stockage** : Les explications ne sont pas sauvegardées (génération à la demande)

### Améliorations Futures

- [ ] Stockage des explications dans la base de données
- [ ] Génération asynchrone pour les méthodes lentes
- [ ] Support de modèles personnalisés
- [ ] Export en PDF des rapports XAI
- [ ] Comparaison côte-à-côte de plusieurs méthodes
- [ ] XAI par classe (explication pour chaque classe de défaut)

---

## 🆘 Dépannage

### Problème : "Grad-CAM not available"

**Cause** : Bibliothèque `pytorch-grad-cam` non installée

**Solution** :
```bash
docker exec mlops_backend pip install grad-cam
docker restart mlops_backend
```

### Problème : Heatmap vide ou noire

**Cause** : Le modèle n'a pas détecté d'objet dans l'image

**Solution** :
- Vérifier que l'image contient bien des objets détectables
- Baisser le seuil de confiance du modèle
- Utiliser une image de test connue (zidane.jpg, bus.jpg)

### Problème : Erreur "Model path not found"

**Cause** : Le modèle spécifié n'existe pas

**Solution** :
- Ne pas spécifier `model_id` pour utiliser yolov8n par défaut
- Vérifier que le modèle existe dans la base de données

### Problème : Interface lente

**Cause** : Image trop grande

**Solution** :
- Redimensionner l'image avant upload (max 1920x1080)
- Utiliser JPEG au lieu de PNG

---

## 📚 Références

### Articles Scientifiques

1. **Grad-CAM**: "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization" (Selvaraju et al., 2017)
2. **Grad-CAM++**: "Grad-CAM++: Improved Visual Explanations for Deep Convolutional Networks" (Chattopadhyay et al., 2018)
3. **LIME**: "Why Should I Trust You? Explaining the Predictions of Any Classifier" (Ribeiro et al., 2016)
4. **Integrated Gradients**: "Axiomatic Attribution for Deep Networks" (Sundararajan et al., 2017)
5. **SHAP**: "A Unified Approach to Interpreting Model Predictions" (Lundberg & Lee, 2017)

### Ressources

- **Documentation Grad-CAM** : https://github.com/jacobgil/pytorch-grad-cam
- **Documentation LIME** : https://github.com/marcotcr/lime
- **Documentation Captum** : https://captum.ai/
- **Documentation SHAP** : https://shap.readthedocs.io/

---

## ✅ Checklist de Déploiement

Avant d'utiliser XAI en production :

- [ ] Backend démarré avec module XAI chargé
- [ ] Bibliothèques XAI installées (`grad-cam` minimum)
- [ ] Test de génération Grad-CAM réussi
- [ ] Interface web accessible sur `/xai`
- [ ] Menu "XAI" visible dans la sidebar
- [ ] Documentation communiquée aux utilisateurs
- [ ] Exemples de bonnes/mauvaises explications préparés

---

**🎉 Le module XAI est maintenant intégré dans votre plateforme MLOps QC !**

Accédez-y via : **http://localhost:3000/xai**
