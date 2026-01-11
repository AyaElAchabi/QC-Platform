# 🎯 Guide de Test - Interface Graphique

## 🚀 Accès Rapide

**URL** : http://localhost:3000

**Identifiants** :
- Email : `eyaelachabi@gmail.com`
- Password : `Eyaelach0200@`

---

## 📱 Étapes de Test

### 1. Connexion
1. Ouvrir http://localhost:3000
2. Entrer les identifiants ci-dessus
3. Cliquer sur "Se connecter"

### 2. Navigation vers Inférence
1. Dans la sidebar gauche, cliquer sur "⚡ Inférence"
2. Vous arrivez sur `/inference/detect`

### 3. Page d'Inférence - Éléments Visuels

**En haut** :
```
┌─────────────────────────────────────────────────┐
│  Détection d'Objets YOLOv8                     │
│  Uploadez une image pour détecter des objets    │
└─────────────────────────────────────────────────┘
```

**Section Configuration** :
```
┌─────────────────────────────────────────────────┐
│  Modèle                                         │
│  [Dropdown: yolov8n_trained ▼]                  │
│                                                  │
│  Seuil de Confiance: 0.25                       │
│  [━━━━━━●━━━━━━━━━━━] 0.25                       │
└─────────────────────────────────────────────────┘
```

**Section Upload** :
```
┌─────────────────────────────────────────────────┐
│             🖼️                                   │
│     Glissez une image ici                       │
│     ou cliquez pour sélectionner                │
│                                                  │
│  Formats supportés: JPG, PNG, JPEG              │
└─────────────────────────────────────────────────┘
```

### 4. Upload d'Image

**Option A - Drag & Drop** :
1. Prendre l'image `test_image.jpg` du dossier du projet
2. La glisser sur la zone de drop
3. L'inférence démarre automatiquement

**Option B - Clic** :
1. Cliquer dans la zone de drop
2. Sélectionner `test_image.jpg`
3. L'inférence démarre automatiquement

### 5. Résultats Attendus

**Canvas avec l'image** :
```
┌─────────────────────────────────────────────────┐
│                                                  │
│         [Image uploadée]                         │
│     (avec bounding boxes si détections)          │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Informations** :
```
Temps d'inférence: ~400-2000 ms
Détections: 0 (pour YOLOv8n de base sur image synthétique)
```

**Tableau des détections** (si objets détectés) :
```
┌──────────┬────────────┬──────────────────────────┐
│  Classe  │ Confiance  │        Position          │
├──────────┼────────────┼──────────────────────────┤
│  person  │   0.87     │  x:120, y:80, w:50, h:100│
│  car     │   0.92     │  x:300, y:200, w:80, h:60│
└──────────┴────────────┴──────────────────────────┘
```

---

## 🧪 Test avec Image Réelle

Pour tester avec des détections réelles (classes COCO) :

1. **Télécharger une image de test COCO** :
   ```bash
   curl -o test_coco.jpg https://ultralytics.com/images/bus.jpg
   ```

2. **Uploader dans l'interface** :
   - Cette image contient : personnes, bus, vélo
   - YOLOv8n devrait détecter ces objets ✅

3. **Résultats attendus** :
   - Plusieurs bounding boxes colorées
   - Tableau avec détections
   - Classes : person, bus, bicycle, etc.

---

## 🎨 Classes COCO (YOLOv8n de base)

Le modèle YOLOv8n détecte 80 classes :

```
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat,
traffic light, fire hydrant, stop sign, parking meter, bench, bird,
cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack,
umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball,
kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket,
bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple,
sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair,
couch, potted plant, bed, dining table, toilet, tv, laptop, mouse,
remote, keyboard, cell phone, microwave, oven, toaster, sink,
refrigerator, book, clock, vase, scissors, teddy bear, hair drier,
toothbrush
```

---

## 🔄 Test de Performance

### Premier Upload (sans cache)
```
1. Uploader image → ~2000 ms
   ↳ Téléchargement modèle depuis MinIO
   ↳ Chargement en mémoire
   ↳ Inférence

2. Cache Redis activé ✅
   ↳ Modèle sauvegardé localement
   ↳ Chemin en cache (1h TTL)
```

### Uploads Suivants (avec cache)
```
1. Uploader image → ~400 ms ⚡
   ↳ Modèle déjà en mémoire
   ↳ Inférence seulement

Performance : 5x plus rapide !
```

---

## 📸 Captures Écran Attendues

### Vue Initiale
```
╔═══════════════════════════════════════════════════╗
║  MLOPS QC Platform                                ║
║  ┌─────────────┐  ┌──────────────────────────────┐║
║  │ Dashboard   │  │  Détection d'Objets YOLOv8    │║
║  │ Projets     │  │                                │║
║  │ Images      │  │  Modèle: yolov8n_trained ▼    │║
║  │ Modèles     │  │  Confiance: [━━●━━━] 0.25     │║
║  │ ⚡ Inférence│  │                                │║
║  │ Reports     │  │  🖼️ Glissez une image ici      │║
║  │ Paramètres  │  │                                │║
║  └─────────────┘  └──────────────────────────────┘║
╚═══════════════════════════════════════════════════╝
```

### Après Upload
```
╔═══════════════════════════════════════════════════╗
║  MLOPS QC Platform                                ║
║  ┌─────────────┐  ┌──────────────────────────────┐║
║  │ Sidebar     │  │  ┌────────────────────────┐   │║
║  │             │  │  │                        │   │║
║  │             │  │  │   [Image + Boxes]      │   │║
║  │             │  │  │                        │   │║
║  │             │  │  └────────────────────────┘   │║
║  │             │  │  Temps: 393 ms               │║
║  │             │  │  Détections: 3               │║
║  │             │  │                              │║
║  │             │  │  Classe   Conf    Position   │║
║  │             │  │  person   0.87    x:120...   │║
║  │             │  │  car      0.92    x:300...   │║
║  └─────────────┘  └──────────────────────────────┘║
╚═══════════════════════════════════════════════════╝
```

---

## ✅ Checklist de Validation

### Fonctionnalités UI
- [ ] Page accessible à `/inference/detect`
- [ ] Dropdown modèle fonctionnel
- [ ] Slider de confiance réactif (0.0 - 1.0)
- [ ] Zone de drop stylée et interactive
- [ ] Upload par clic fonctionne
- [ ] Upload par drag & drop fonctionne
- [ ] Canvas affiche l'image
- [ ] Bounding boxes dessinées (si détections)
- [ ] Tableau des détections affiché
- [ ] Temps d'inférence affiché
- [ ] Messages d'erreur clairs

### Performance
- [ ] Premier upload : 1-3 secondes
- [ ] Uploads suivants : < 1 seconde
- [ ] Pas de freeze de l'UI
- [ ] Loading spinner visible

### Cas d'Erreur
- [ ] Modèle non sélectionné → Message d'erreur
- [ ] Image invalide → Message d'erreur
- [ ] Erreur API → Message d'erreur clair

---

## 🎯 Prochaines Actions Recommandées

### 1. Entraîner un Modèle Personnalisé (Optionnel)
Pour détecter VOS objets spécifiques :

```
1. Aller dans "Projets"
2. Créer/Sélectionner un projet
3. Uploader des images
4. Annoter les images (Label Studio)
5. Aller dans "Modèles" → "Entraîner un modèle"
6. Configurer : epochs=10, batch=16, lr=0.01
7. Lancer training
8. Attendre fin training (~5-30 min selon dataset)
9. Le modèle sera automatiquement uploadé dans MinIO ✅
10. Utiliser le nouveau modèle dans Inférence
```

### 2. Tester avec Images Variées
```bash
# Images de test COCO
curl -o bus.jpg https://ultralytics.com/images/bus.jpg
curl -o zidane.jpg https://ultralytics.com/images/zidane.jpg

# Upload dans l'interface
# Devrait détecter : personnes, véhicules, objets
```

### 3. Monitorer les Performances
```bash
# Vérifier cache Redis
docker exec -it mlops_redis redis-cli
> KEYS model_path:*
> TTL model_path:1b62d2d1-ded3-4205-8251-d9412ab7cd00
> GET model_path:1b62d2d1-ded3-4205-8251-d9412ab7cd00

# Vérifier historique
curl -X GET "http://localhost:8000/api/inference/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Dépannage

### Problème : "Aucun modèle disponible"
**Solution** : Vérifier que le modèle existe en DB et dans MinIO
```bash
python3 fix-existing-model.py
```

### Problème : Inférence très lente (>5 sec)
**Solution** : 
1. Vérifier cache Redis actif
2. Redémarrer backend : `docker-compose restart backend`
3. Première inférence toujours plus lente (normale)

### Problème : Erreur 404
**Solution** : Vérifier que backend est démarré
```bash
curl http://localhost:8000/health
# Devrait retourner : {"status":"healthy"}
```

### Problème : Image ne s'affiche pas
**Solution** : 
1. Vérifier format (JPG/PNG seulement)
2. Vérifier taille (< 10 MB recommandé)
3. Ouvrir console navigateur (F12) pour erreurs JS

---

## 📞 Support

**Logs Frontend** :
```bash
# Dans le navigateur
F12 → Console
```

**Logs Backend** :
```bash
docker-compose logs backend --tail=50 -f
```

**Tester API directement** :
```bash
./test-inference-complete.sh
```

---

**Date** : 20 Novembre 2025  
**Status** : ✅ Interface Fonctionnelle  
**Prochaine étape** : Tester visuellement dans le navigateur
