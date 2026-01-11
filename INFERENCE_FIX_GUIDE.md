# 🔍 GUIDE - Page d'Inférence Améliorée

## ✅ MODIFICATIONS APPORTÉES

### 1. Affichage des Résultats Amélioré ⭐

**Ce qui a été ajouté:**
- ✅ Canvas avec bounding boxes plus visibles (bordure épaisse)
- ✅ Encadrement des défauts détectés en couleur
- ✅ Labels avec nom de classe et confiance
- ✅ Résumé visuel des détections (carte bleue)
- ✅ Tableau détaillé avec barres de progression

### 2. Explications Visuelles (XAI) ✅

**Déjà présent dans le code:**
- ✅ Toggle "Explications (XAI)" dans la configuration
- ✅ Heatmap d'attention (carte d'activation)
- ✅ Métriques de confiance (moyenne, min, max)
- ✅ Distribution par classe
- ✅ Distribution spatiale (centre vs bords)

### 3. Bouton XAI par Détection ✅

**Composant DetectionXAI:**
- ✅ Bouton "Expliquer" pour chaque détection
- ✅ Modal avec analyse Grad-CAM, SHAP, LIME
- ✅ Explications détaillées par défaut

### 4. Debug Amélioré 🐛

**Logs console ajoutés:**
- `🚀 Envoi requête d'inférence...`
- `📡 Réponse reçue: 200`
- `✅ Données reçues: {...}`
- `🔥 Heatmap reçue`
- `📊 Métriques XAI reçues`

---

## 🎯 COMMENT UTILISER

### Étape 1: Accéder à la Page d'Inférence

```
1. Connectez-vous sur http://localhost:3000
2. Cliquez sur "Inférence" dans le menu latéral
3. Vous arrivez sur /inference/detect
```

### Étape 2: Configuration

```
1. Sélectionner un Modèle
   → Choisir un modèle entraîné dans la liste

2. Ajuster le Seuil de Confiance
   → Curseur de 10% à 90%
   → Par défaut: 25%

3. Activer les Explications XAI (optionnel)
   → Toggle "Explications (XAI)"
   → ⚠️ Ajoute 500-1000ms au temps d'inférence
```

### Étape 3: Upload et Détection

```
1. Cliquer sur la zone d'upload
2. Sélectionner une image (JPG, PNG)
3. Cliquer sur "Détecter les Défauts"
4. Attendre le résultat...
```

### Étape 4: Résultats Affichés

```
✅ Image avec Bounding Boxes
   - Rectangles colorés autour des défauts
   - Labels avec classe + confiance

✅ Résumé des Détections
   - Nombre de défauts
   - Confiance moyenne
   - Temps d'inférence

✅ Tableau Détaillé
   - Classe de chaque défaut
   - Barre de progression de confiance
   - Position (bbox coordinates)
   - Bouton "Expliquer" (XAI)
```

### Étape 5: Explications XAI (si activé)

```
✅ Heatmap d'Attention
   - Carte colorée montrant où le modèle regarde
   - Rouge/jaune = haute attention
   - Bleu = basse attention

✅ Statistiques de Confiance
   - Moyenne: X%
   - Min / Max: X% / Y%

✅ Distribution par Classe
   - Nombre de détections par classe
   - Confiance moyenne par classe

✅ Distribution Spatiale
   - Nombre au centre vs bords
```

### Étape 6: XAI Avancé (par détection)

```
1. Cliquer sur "Expliquer" dans le tableau
2. Modal s'ouvre avec:
   - Grad-CAM (carte d'activation)
   - SHAP values (contribution des features)
   - LIME (explication locale)
   - Integrated Gradients
3. Explications textuelles détaillées
```

---

## 🎨 CE QUI DEVRAIT S'AFFICHER

### Vue Normale (Sans Détection)

```
┌─────────────────────────────────────────┐
│  Configuration          │  Résultats    │
├─────────────────────────┼───────────────┤
│  [Modèle]              │               │
│  [Seuil: 25%]          │  [Upload]     │
│  [⚪ Explications]      │   Icon        │
│  [Upload Image]         │  "Uploadez    │
│  [Détecter]            │   une image"  │
└─────────────────────────┴───────────────┘
```

### Vue Avec Détections

```
┌─────────────────────────────────────────┐
│  Configuration          │  Résultats    │
├─────────────────────────┼───────────────┤
│  [yolov8n]             │ ┌─────────────┐│
│  [Seuil: 25%]          │ │ Image avec  ││
│  [🔵 Explications]      │ │ Boxes       ││
│  [scratches_300.jpg]    │ │ rouges/     ││
│  [✅ Détecté]           │ │ vertes      ││
│                         │ └─────────────┘│
│                         │                │
│                         │ 📊 2 défauts   │
│                         │ Confiance: 85% │
│                         │ ⚡ 120ms        │
│                         │                │
│                         │ [Tableau]      │
│                         │ Classe | Conf  │
│                         │ scratch| 92%   │
│                         │ dent   | 78%   │
└─────────────────────────┴───────────────┘

┌─────────────────────────────────────────┐
│  📊 Explications (XAI)                  │
├─────────────────────────────────────────┤
│  🔥 Carte d'Attention                   │
│  [Heatmap Image]                        │
│                                         │
│  📈 Statistiques                        │
│  Moyenne: 85%  Min/Max: 78% / 92%      │
│                                         │
│  📊 Distribution                         │
│  scratch: 1 (92%)                       │
│  dent: 1 (78%)                          │
│                                         │
│  📍 Spatial: Centre: 1, Bords: 1       │
└─────────────────────────────────────────┘
```

---

## 🐛 RÉSOLUTION DES PROBLÈMES

### Problème 1: "Rien ne s'affiche après détection"

**Causes possibles:**
1. API backend ne retourne pas les détections
2. Erreur JavaScript dans la console
3. Canvas ne se dessine pas

**Solutions:**
```bash
# 1. Ouvrir la Console du navigateur (F12)
# 2. Regarder les logs:
#    - 🚀 Envoi requête...
#    - 📡 Réponse reçue: 200
#    - ✅ Données reçues: {...}

# 3. Vérifier si des détections sont reçues:
console.log("Détections:", detections)

# 4. Vérifier l'API backend:
curl -X POST http://localhost:8000/api/inference/predict \
  -H "Authorization: Bearer TOKEN" \
  -F "image=@image.jpg" \
  -F "model_id=model-id"
```

### Problème 2: "Image uploaded mais pas de boxes"

**Cause:** Le canvas ne dessine pas les boxes

**Solution:**
```javascript
// Vérifier dans la console:
// 1. detections.length > 0 ?
// 2. drawDetections() appelé ?
// 3. Canvas dimensions correctes ?

// Forcer le redraw:
setTimeout(() => drawDetections(), 500)
```

### Problème 3: "XAI ne s'affiche pas"

**Cause:** Toggle XAI non activé ou backend ne génère pas XAI

**Solution:**
```
1. Activer le toggle "Explications (XAI)" AVANT de détecter
2. Vérifier les logs:
   - 🔥 Heatmap reçue
   - 📊 Métriques XAI reçues
3. Si absent, vérifier le backend
```

### Problème 4: "Erreur 403 ou 500"

**Cause:** Token invalide ou erreur backend

**Solution:**
```bash
# 1. Se reconnecter
# 2. Vérifier les logs backend:
docker logs mlops_backend --tail 50

# 3. Tester l'API directement:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

---

## 📸 CAPTURES D'ÉCRAN ATTENDUES

### 1. Configuration

- ✅ Liste déroulante des modèles
- ✅ Slider de confiance (0-100%)
- ✅ Toggle XAI avec warning orange
- ✅ Zone d'upload avec nom de fichier
- ✅ Bouton "Détecter les Défauts"

### 2. Résultats

- ✅ Image avec rectangles colorés
- ✅ Labels sur les boxes (classe + %)
- ✅ Carte bleue résumé (X défauts, Y% confiance)
- ✅ Tableau avec colonnes: Classe | Confiance | Position | Actions
- ✅ Barres de progression dans le tableau

### 3. Explications XAI

- ✅ Section séparée en bas
- ✅ Heatmap colorée (bleu→rouge)
- ✅ Statistiques avec cartes blanches
- ✅ Distribution par classe avec badges
- ✅ Distribution spatiale (2 colonnes)

### 4. Modal XAI Avancé

- ✅ Bouton "Expliquer" cliqué
- ✅ Modal avec onglets (Grad-CAM, SHAP, LIME)
- ✅ Visualisations pour chaque méthode
- ✅ Texte explicatif

---

## 🧪 TEST RAPIDE

```bash
# 1. Ouvrir la page
open http://localhost:3000/inference/detect

# 2. Vérifier la console (F12)
# 3. Upload une image de test
# 4. Activer XAI
# 5. Cliquer "Détecter"
# 6. Observer les logs console:
#    🚀 → 📡 → ✅ → 🔥 → 📊

# 7. Vérifier que tout s'affiche:
#    ✅ Image avec boxes
#    ✅ Résumé bleu
#    ✅ Tableau
#    ✅ Panel XAI en bas
```

---

## 📚 FICHIERS MODIFIÉS

| Fichier | Modification |
|---------|--------------|
| `frontend/src/app/(app)/inference/detect/page.tsx` | Logs debug + affichage amélioré |
| `frontend/src/components/inference/ExplainabilityPanel.tsx` | Panel XAI (déjà présent) |
| `frontend/src/components/inference/DetectionXAI.tsx` | Modal XAI avancé (déjà présent) |

---

## ✅ CHECKLIST

- [x] Code modifié avec logs debug
- [x] Affichage résultats amélioré
- [x] Canvas avec boxes colorés
- [x] Résumé des détections (carte bleue)
- [x] Tableau détaillé avec progress bars
- [x] Panel XAI (heatmap + métriques)
- [x] Bouton XAI par détection
- [x] Documentation créée

---

**🎉 Testez maintenant et regardez la console du navigateur (F12) pour les logs !**
