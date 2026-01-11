# 🎯 Guide d'Intégration XAI - Approche Contextuelle

## Philosophie XAI

### ✨ Principes de Conception

**XAI est OPTIONNELLE et CONTEXTUELLE**
```
❌ PAS comme ça :
- Page séparée déconnectée des prédictions
- XAI systématique sur toutes les images
- Graphiques abstraits sans lien avec la détection

✅ MAIS comme ça :
- Bouton "Expliquer" par détection
- Déclenchée volontairement par l'utilisateur
- Visualisation liée à UNE détection spécifique
- Comparaison image originale ↔ heatmap
```

---

## 🔄 Flux Utilisateur

### Scénario 1 : Inférence Normale (Sans XAI)

```
1. Upload image
2. Clic "Détecter"
3. Voir les résultats (bounding boxes + tableau)
4. FIN ✅
```

**Temps total** : ~100-200ms
**Coût** : Minimal

### Scénario 2 : Inférence + Explication (Avec XAI)

```
1. Upload image
2. Clic "Détecter"
3. Voir les résultats
4. Clic "Expliquer" sur UNE détection spécifique 👈
5. Dialog s'ouvre avec :
   - Image originale + bbox
   - Heatmap Grad-CAM
   - Comparaison côte-à-côte
   - Métriques de la détection
6. Téléchargement optionnel
7. FIN ✅
```

**Temps total** : ~100-200ms (inférence) + ~500-1000ms (XAI sur demande)
**Coût** : Payé uniquement si demandé

---

## 🎨 Interface Utilisateur

### Page d'Inférence : `/inference/detect`

#### **Avant (Sans XAI)**
```
┌────────────────────────────────────────┐
│ Classe      │ Confiance │ Position     │
├────────────────────────────────────────┤
│ Scratches   │ 95.3%     │ [10,20,50,60]│
│ Rolled-in   │ 87.1%     │ [100,5,150,80]│
└────────────────────────────────────────┘
```

#### **Après (Avec XAI)**
```
┌─────────────────────────────────────────────────────┐
│ Classe      │ Confiance │ Position     │ Actions    │
├─────────────────────────────────────────────────────┤
│ Scratches   │ 95.3%     │ [10,20,50,60]│ [Expliquer]│
│ Rolled-in   │ 87.1%     │ [100,5,150,80]│ [Expliquer]│
└─────────────────────────────────────────────────────┘
```

### Dialog XAI (Quand "Expliquer" est cliqué)

```
╔═══════════════════════════════════════════════════════╗
║  🌟 Explication XAI - Scratches                       ║
║  Pourquoi le modèle a détecté "Scratches" (95.3%)    ║
╠═══════════════════════════════════════════════════════╣
║                                                        ║
║  ℹ️  Comment interpréter :                            ║
║  Les zones rouges/oranges indiquent les régions qui   ║
║  ont influencé la détection.                          ║
║                                                        ║
║  [Comparaison] [Grad-CAM] [Grad-CAM++]                ║
║                                                        ║
║  ┌──────────────┬──────────────┐                      ║
║  │   Original   │   Grad-CAM   │                      ║
║  │              │              │                      ║
║  │  [Image +    │  [Heatmap    │                      ║
║  │   bbox]      │   overlay]   │                      ║
║  │              │              │                      ║
║  └──────────────┴──────────────┘                      ║
║                                                        ║
║  📊 Détails de la détection                           ║
║  Classe : Scratches                                   ║
║  Confiance : 95.30%                                   ║
║  Position : [10, 20, 50, 60]                          ║
║  Méthode XAI : Grad-CAM                               ║
║                                                        ║
║                         [Télécharger] [Fermer]        ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🔧 Architecture Technique

### Composants Frontend

#### 1. **DetectionXAI.tsx**
**Rôle** : Composant réutilisable pour chaque détection

```tsx
<DetectionXAI
  imageUrl={imagePreview}
  detection={{
    class: "Scratches",
    confidence: 0.953,
    bbox: [10, 20, 50, 60]
  }}
  modelId="model-uuid"
/>
```

**Rendu** :
- Bouton "Expliquer" (petit, discret)
- Dialog qui s'ouvre au clic
- Génération XAI à la demande (lazy loading)

#### 2. **Page d'Inférence**
**Fichier** : `frontend/src/app/(app)/inference/detect/page.tsx`

**Intégration** :
```tsx
{detections.map((detection, idx) => (
  <tr key={idx}>
    <td>{detection.class_name}</td>
    <td>{detection.confidence}%</td>
    <td>{detection.bbox}</td>
    <td>
      <DetectionXAI
        imageUrl={imagePreview}
        detection={detection}
        modelId={selectedModel}
      />
    </td>
  </tr>
))}
```

### Backend API

#### Endpoint : POST /api/xai/generate

**Requête** :
```json
{
  "image_path": "data:image/png;base64,...",
  "methods": ["gradcam"],
  "model_id": "uuid",
  "bbox": [10, 20, 50, 60]  // Optionnel : focus sur bbox
}
```

**Réponse** :
```json
{
  "explanations": {
    "gradcam": {
      "method": "gradcam",
      "heatmap": "data:image/png;base64,...",
      "success": true
    }
  },
  "image_path": "...",
  "model_id": "uuid"
}
```

---

## 📊 Cas d'Usage

### 1. **Validation d'une Détection Suspecte**

**Contexte** : Le modèle détecte un défaut avec 65% de confiance (incertain)

**Action** :
1. Clic sur "Expliquer" pour cette détection
2. Voir la heatmap Grad-CAM
3. Vérifier si les zones rouges correspondent au défaut

**Décision** :
- ✅ Zones rouges sur le défaut → Confiance validée
- ❌ Zones rouges ailleurs → Faux positif probable

### 2. **Compréhension d'un Faux Positif**

**Contexte** : Le modèle détecte "Scratch" là où il n'y en a pas

**Action** :
1. Clic "Expliquer"
2. Voir que la heatmap active une zone avec un reflet/ombre
3. Comprendre la confusion

**Solution** : Ajouter des exemples similaires en négatif au training set

### 3. **Audit Qualité**

**Contexte** : Besoin de prouver que le modèle prend de bonnes décisions

**Action** :
1. Pour chaque défaut critique détecté, générer l'explication
2. Télécharger les heatmaps
3. Créer un rapport : Image → Détection → Explication

**Résultat** : Dossier d'audit pour certification

### 4. **Formation des Opérateurs**

**Contexte** : Nouveaux opérateurs doivent comprendre le modèle

**Action** :
1. Créer une bibliothèque d'exemples typiques
2. Pour chaque exemple, afficher l'explication
3. Montrer ce que le modèle "voit"

**Résultat** : Opérateurs capables de juger la fiabilité

---

## 🎯 Avantages de l'Approche Contextuelle

### ✅ Performance
- **XAI générée uniquement sur demande**
- Pas de surcoût si non utilisée
- Inférence reste rapide (~100-200ms)

### ✅ Ergonomie
- **Optionnelle** : L'utilisateur décide
- **Ciblée** : Une détection à la fois
- **Visuelle** : Comparaison directe image ↔ heatmap

### ✅ Pertinence
- **Contextuelle** : Liée à UNE décision spécifique
- **Actionnable** : L'utilisateur peut valider/invalider
- **Compréhensible** : Pas de graphiques abstraits

### ✅ Scalabilité
- **Lazy loading** : Génération à la demande
- **Cacheable** : Peut être stockée si récurrente
- **Pas de batch** : Évite les calculs inutiles

---

## 🚀 Comment Utiliser

### Étape 1 : Exécuter une Inférence
```
1. Aller sur /inference/detect
2. Uploader une image
3. Sélectionner un modèle
4. Cliquer "Détecter"
```

### Étape 2 : Expliquer une Détection
```
5. Dans le tableau des résultats, trouver une détection
6. Cliquer sur le bouton "Expliquer" 🌟
7. Le dialog s'ouvre avec :
   - Onglet "Comparaison" : Image vs Heatmap
   - Onglet "Grad-CAM" : Heatmap seule
   - Onglet "Grad-CAM++" : Version améliorée
```

### Étape 3 : Interpréter
```
8. Vérifier que les zones rouges/jaunes correspondent au défaut
9. Lire les métriques (classe, confiance, position)
10. Optionnel : Télécharger la heatmap
```

---

## 📝 Bonnes Pratiques

### ✅ À FAIRE
- Utiliser XAI sur des détections **incertaines** (confiance 50-70%)
- Expliquer les **faux positifs** pour comprendre l'erreur
- Créer des **rapports d'audit** avec XAI pour les défauts critiques
- Former les opérateurs avec des **exemples XAI**

### ❌ À ÉVITER
- Générer XAI sur **toutes** les détections (coût temps)
- Utiliser XAI sur des détections **évidentes** (confiance > 95%)
- Ignorer les heatmaps qui n'activent **pas le défaut** (faux positifs)
- Stocker **toutes** les explications (coût stockage)

---

## 🔬 Interprétation des Heatmaps

### Bonne Explication ✅
```
Image : Defect "Scratch" à 89% de confiance
Heatmap : Zones rouges concentrées SUR le scratch

Interprétation :
→ Le modèle a bien identifié le défaut
→ La décision est fiable
→ Confiance justifiée
```

### Explication Douteuse ⚠️
```
Image : Defect "Patch" à 68% de confiance
Heatmap : Zones rouges dispersées + activation du fond

Interprétation :
→ Le modèle hésite
→ Activation partielle du défaut
→ Décision à vérifier manuellement
```

### Mauvaise Explication ❌
```
Image : Defect "Inclusion" à 92% de confiance
Heatmap : Zones rouges sur un reflet, PAS sur le défaut

Interprétation :
→ Faux positif évident
→ Le modèle confond reflet et défaut
→ Ajouter des exemples négatifs au training
```

---

## 🛠️ Fichiers Modifiés

### Frontend
- ✅ **Créé** : `frontend/src/components/inference/DetectionXAI.tsx`
- ✅ **Modifié** : `frontend/src/app/(app)/inference/detect/page.tsx`
- ✅ **Conservé** : `frontend/src/app/(app)/xai/page.tsx` (pour tests)

### Backend
- ✅ **Créé** : `backend/services/xai/xai_service.py`
- ✅ **Créé** : `backend/api/routes/xai.py`
- ✅ **Modifié** : `backend/api/main.py` (route XAI ajoutée)

---

## 📌 Prochaines Étapes (Optionnel)

### Phase 1 : Optimisation
- [ ] Cache des explications (éviter regénération)
- [ ] Génération asynchrone (non bloquante)
- [ ] Préchargement des heatmaps courantes

### Phase 2 : Enrichissement
- [ ] LIME et Integrated Gradients
- [ ] Score de consensus (moyenne de plusieurs méthodes)
- [ ] Incertitude (variance entre méthodes)

### Phase 3 : Analyse
- [ ] Stockage des explications en base
- [ ] Statistiques : % d'explications demandées
- [ ] Corrélation XAI ↔ erreurs du modèle

---

## ✅ Checklist

- [x] Composant `DetectionXAI` créé
- [x] Intégré dans la page d'inférence
- [x] Bouton "Expliquer" par détection
- [x] Dialog avec comparaison côte-à-côte
- [x] Téléchargement des heatmaps
- [x] Backend XAI fonctionnel
- [x] Documentation complète

---

**🎉 XAI est maintenant intégré de manière contextuelle et optionnelle !**

**Testez-le** :
1. Allez sur http://localhost:3000/inference/detect
2. Uploadez une image et détectez
3. Cliquez "Expliquer" sur une détection
4. Comparez image ↔ heatmap

**Principe clé** : XAI déclenchée **volontairement**, **jamais imposée**.
