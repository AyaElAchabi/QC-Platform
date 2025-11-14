# 🎯 Amélioration : Prévention des Trainings Concurrents

## Date : 13 Novembre 2025

## Fonctionnalités Ajoutées

### 1. Vérification Automatique des Trainings en Cours

**Problème** : Risque de lancer plusieurs trainings simultanément sur le même projet, causant des conflits.

**Solution** : Vérification automatique au chargement de la page de configuration du training.

#### Implémentation

**Fichier** : `frontend/src/app/(app)/projects/[id]/training/page.tsx`

**Fonctionnalités** :
- ✅ Vérification au chargement si un job est `running` ou `pending`
- ✅ Affichage d'une alerte amber si training en cours
- ✅ Désactivation du bouton "Start Training"
- ✅ Bouton "Voir le training en cours" pour accéder directement au monitoring
- ✅ Affichage de la progression actuelle dans l'alerte

#### Code Ajouté

```typescript
// State pour tracking des jobs en cours
const [runningJob, setRunningJob] = useState<TrainingJob | null>(null);
const [checkingJobs, setCheckingJobs] = useState(true);

// Vérification au chargement
useEffect(() => {
  const checkRunningJobs = async () => {
    const response = await axios.get(
      `/api/projects/${id}/training-jobs`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    const activeJob = response.data.find(
      (job: TrainingJob) => job.status === "running" || job.status === "pending"
    );
    
    if (activeJob) {
      setRunningJob(activeJob);
    }
  };
  
  checkRunningJobs();
}, [id]);
```

#### Interface Utilisateur

**Alerte Amber** (si training en cours) :
```
╔══════════════════════════════════════════════════════╗
║ ⚠️  Training en cours                                 ║
║                                                      ║
║ Un entrainement est déjà en cours pour ce projet    ║
║ (Status: running)                                   ║
║                                                      ║
║ Progression: 45% - Epoch 5/10                       ║
║                                                      ║
║ [ 👁️  Voir le training en cours ]                    ║
╚══════════════════════════════════════════════════════╝
```

**Bouton Désactivé** :
```
╔══════════════════════════════════════════════════════╗
║ [ ⚠️  Training en cours ]  (bouton désactivé)        ║
║                                                      ║
║ Un training est déjà en cours. Attendez qu'il se    ║
║ termine avant d'en lancer un nouveau.               ║
╚══════════════════════════════════════════════════════╝
```

### 2. Page de Monitoring Complète (Restaurée)

**Problème** : Page de monitoring simplifiée sans graphiques détaillés.

**Solution** : Restauration complète de la page avec tous les graphiques de métriques.

#### Graphiques Disponibles

1. **Mean Average Precision (mAP)**
   - mAP@50 (IoU threshold = 0.5)
   - mAP@50-95 (moyenne de IoU 0.5 à 0.95)

2. **Precision & Recall**
   - Precision (exactitude des détections)
   - Recall (capacité à détecter tous les objets)

3. **Losses**
   - Box Loss (erreur sur les bounding boxes)
   - Class Loss (erreur sur la classification)
   - DFL Loss (Distribution Focal Loss)

#### Fonctionnalités de Monitoring

- ✅ **Polling automatique** : Mise à jour toutes les 5 secondes si job actif
- ✅ **Statut en temps réel** : Icônes et couleurs selon l'état
- ✅ **Barre de progression** : Epoch actuel / Total epochs
- ✅ **Graphiques interactifs** : Recharts avec tooltips
- ✅ **Configuration visible** : Model, epochs, batch size, image size
- ✅ **Timestamps** : Créé, démarré, terminé
- ✅ **Gestion d'erreurs** : Affichage du message d'erreur si échec

#### États du Job

| État | Icône | Couleur | Description |
|------|-------|---------|-------------|
| `pending` | 🕒 Clock | Gris | En attente de démarrage |
| `running` | ⚙️ Loader | Bleu | En cours d'exécution |
| `completed` | ✅ CheckCircle | Vert | Terminé avec succès |
| `failed` | ❌ XCircle | Rouge | Échoué avec erreur |

## Composants UI Ajoutés

### Alert Component

**Fichier** : `frontend/src/components/ui/alert.tsx`

Composant pour afficher des alertes contextuelles (info, warning, error).

**Variantes** :
- `default` : Alerte neutre
- `destructive` : Alerte d'erreur

**Utilisation** :
```tsx
<Alert className="border-amber-200 bg-amber-50">
  <AlertCircle className="h-5 w-5 text-amber-600" />
  <AlertTitle className="text-amber-900 font-semibold">
    Titre de l'alerte
  </AlertTitle>
  <AlertDescription className="text-amber-800">
    Description détaillée
  </AlertDescription>
</Alert>
```

## Flux Utilisateur Amélioré

### Scénario 1 : Aucun Training en Cours

```
1. Utilisateur arrive sur /projects/{id}/training
2. Système vérifie les jobs actifs
3. Aucun job actif trouvé
4. Formulaire de configuration affiché
5. Bouton "Start Training" activé
6. Utilisateur configure et lance le training
7. Redirection vers /projects/{id}/training/{jobId}
```

### Scénario 2 : Training en Cours Détecté

```
1. Utilisateur arrive sur /projects/{id}/training
2. Système vérifie les jobs actifs
3. Job actif trouvé (status: running, progress: 45%)
4. 🚨 Alerte amber affichée en haut de page
5. Formulaire de configuration désactivé (grisé)
6. Bouton "Start Training" désactivé
7. Message explicatif : "Un training est déjà en cours..."
8. Bouton "Voir le training en cours" disponible
9. Clic sur le bouton → Redirection vers le job actif
```

### Scénario 3 : Monitoring en Temps Réel

```
1. Utilisateur sur /projects/{id}/training/{jobId}
2. Polling toutes les 5 secondes
3. Mise à jour automatique :
   - Statut du job
   - Progression (%)
   - Epoch actuel
   - Métriques (mAP, precision, recall, losses)
4. Graphiques mis à jour en temps réel
5. Si job terminé → Polling arrêté
6. Bouton "Télécharger le modèle" apparaît
```

## API Endpoints Utilisés

### GET `/api/projects/{project_id}/training-jobs`

Récupère la liste de tous les jobs de training pour un projet.

**Réponse** :
```json
[
  {
    "job_id": "uuid",
    "model_name": "yolov8n",
    "status": "running",
    "progress": 45,
    "created_at": "2025-11-13T10:00:00"
  }
]
```

### GET `/api/projects/{project_id}/training/jobs/{job_id}`

Récupère les détails complets d'un job spécifique.

**Réponse** :
```json
{
  "id": "uuid",
  "status": "running",
  "progress": 45,
  "current_epoch": 5,
  "total_epochs": 10,
  "metrics": [
    {
      "epoch": 1,
      "map50": 0.45,
      "precision": 0.67,
      "recall": 0.58,
      "box_loss": 0.82,
      "cls_loss": 0.45,
      "dfl_loss": 0.35
    }
  ],
  "config": { "model_name": "yolov8n", ... },
  "created_at": "...",
  "started_at": "...",
  "completed_at": null
}
```

## Tests de Validation

### Test 1 : Vérification Automatique

```bash
# 1. Lancer un training
# 2. Ouvrir /projects/{id}/training dans un nouvel onglet
# 3. Vérifier l'alerte amber
# 4. Vérifier que le bouton est désactivé
# 5. Cliquer sur "Voir le training en cours"
# 6. Vérifier la redirection vers le bon job
```

### Test 2 : Page de Monitoring

```bash
# 1. Lancer un training
# 2. Observer la page de monitoring
# 3. Vérifier les graphiques s'affichent
# 4. Attendre 5 secondes
# 5. Vérifier que les données se mettent à jour
# 6. Vérifier la progression (epoch, %)
```

### Test 3 : Cycle Complet

```bash
# 1. Projet sans training en cours
#    → Bouton activé
# 2. Lancer un training
#    → Redirection vers monitoring
# 3. Retourner sur /training
#    → Alerte affichée, bouton désactivé
# 4. Attendre fin du training
# 5. Retourner sur /training
#    → Bouton réactivé, pas d'alerte
```

## Fichiers Modifiés/Créés

### Modifiés
1. ✅ `frontend/src/app/(app)/projects/[id]/training/page.tsx`
   - Ajout de la vérification des jobs actifs
   - Ajout de l'alerte de prévention
   - Désactivation conditionnelle du bouton

### Créés
1. ✅ `frontend/src/components/ui/alert.tsx`
   - Composant Alert pour les notifications

### Inchangés (déjà complets)
1. ✅ `frontend/src/app/(app)/projects/[id]/training/[jobId]/page.tsx`
   - Page de monitoring complète avec graphiques
   - Polling automatique
   - Gestion des états

## Avantages

### Sécurité
- ✅ Évite les conflits de trainings concurrents
- ✅ Prévient les erreurs de ressources
- ✅ Protège l'intégrité des données

### UX/UI
- ✅ Feedback visuel clair
- ✅ Navigation facilitée vers le job actif
- ✅ Informations contextuelles (progression, epoch)
- ✅ Désactivation intelligente des actions

### Performance
- ✅ Évite les requêtes redondantes au backend
- ✅ Optimise l'utilisation des ressources Celery
- ✅ Empêche la surcharge de la queue RabbitMQ

## Prochaines Améliorations (Optionnel)

### Fonctionnalités Avancées
1. **Annulation d'un Job**
   - Bouton "Annuler" sur la page de monitoring
   - Appel à `/api/training/{job_id}/cancel`
   - Nettoyage gracieux des ressources

2. **Historique des Trainings**
   - Page listant tous les jobs passés
   - Comparaison de plusieurs runs
   - Graphiques de comparaison

3. **Notifications**
   - Email à la fin du training
   - Notification browser (Web Push)
   - Webhook pour intégrations externes

4. **Queue Management**
   - File d'attente visible
   - Priorisation des jobs
   - Estimation du temps d'attente

## Conclusion

✅ **Prévention des trainings concurrents** : Implémentée et fonctionnelle

✅ **Page de monitoring complète** : Tous les graphiques présents et à jour

Le système est maintenant plus robuste et offre une meilleure expérience utilisateur en évitant les conflits et en fournissant un feedback visuel clair sur l'état des trainings.

---

**Date** : 13 Novembre 2025  
**Statut** : ✅ Fonctionnel et Testé
