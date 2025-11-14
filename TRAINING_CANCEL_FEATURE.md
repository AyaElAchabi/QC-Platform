# 🛑 Fonctionnalité d'Annulation de Training

**Date**: 13 novembre 2025

## 📝 Description

Ajout de la possibilité d'arrêter un training YOLOv8 en cours d'exécution depuis l'interface utilisateur, permettant de relancer un nouveau training avec des paramètres différents.

## ✨ Fonctionnalités Ajoutées

### 1. Endpoint Backend - Annulation de Training

**Fichier**: `backend/api/routes/training.py`

**Endpoint**: `POST /api/projects/{project_id}/training/jobs/{job_id}/cancel`

**Fonctionnalités**:
- ✅ Révocation de la tâche Celery active
- ✅ Mise à jour du statut du job en "cancelled"
- ✅ Enregistrement de l'epoch d'annulation
- ✅ Gestion des erreurs si la tâche n'existe pas

**Code**:
```python
@router.post("/api/projects/{project_id}/training/jobs/{job_id}/cancel")
async def cancel_training_job(
    project_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Annuler un training en cours"""
    
    # Vérifier que le job existe et est annulable
    if job.status not in ["pending", "running"]:
        raise HTTPException(400, "Cannot cancel completed/failed job")
    
    # Révoquer la tâche Celery
    celery_app.control.revoke(str(job.id), terminate=True, signal='SIGKILL')
    
    # Marquer comme annulé
    job.status = "cancelled"
    job.completed_at = datetime.utcnow()
    
    return {"status": "cancelled", "message": "Training cancelled"}
```

### 2. Interface Frontend - Bouton d'Annulation

**Fichier**: `frontend/src/app/(app)/projects/[id]/training/page.tsx`

**Ajouts**:

#### a) État de Gestion
```typescript
const [isCancelling, setIsCancelling] = useState(false);
```

#### b) Fonction d'Annulation
```typescript
const handleCancelTraining = async () => {
  if (!confirm("Êtes-vous sûr ?")) return;
  
  setIsCancelling(true);
  
  try {
    await axios.post(
      `/api/projects/${id}/training/jobs/${runningJob.job_id}/cancel`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    setRunningJob(null);
    alert("Training annulé avec succès !");
  } catch (error) {
    alert("Erreur lors de l'annulation");
  } finally {
    setIsCancelling(false);
  }
};
```

#### c) Bouton UI
```tsx
<Button
  variant="destructive"
  size="sm"
  onClick={handleCancelTraining}
  disabled={isCancelling}
>
  {isCancelling ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Annulation...
    </>
  ) : (
    "Arrêter et relancer"
  )}
</Button>
```

## 🎨 Interface Utilisateur

### Alerte de Training en Cours (Mise à Jour)

**Avant**:
```
┌─────────────────────────────────────────┐
│ ⚠️  Training en cours                    │
│                                         │
│ Un entrainement est déjà en cours       │
│ Progression: 0% - Epoch 0/10            │
│                                         │
│ [👁️  Voir le training en cours]         │
└─────────────────────────────────────────┘
```

**Après**:
```
┌─────────────────────────────────────────┐
│ ⚠️  Training en cours                    │
│                                         │
│ Un entrainement est déjà en cours       │
│ Progression: 0% - Epoch 0/10            │
│                                         │
│ [👁️  Voir le training]  [🛑 Arrêter]    │
└─────────────────────────────────────────┘
```

### États du Bouton

1. **Normal**: "Arrêter et relancer" (bouton rouge destructive)
2. **Chargement**: "Annulation..." avec spinner animé
3. **Désactivé**: Pendant l'annulation (disabled=true)

## 🔄 Flux d'Utilisation

### Scénario 1 : Annuler et Relancer
```
1. Utilisateur voit l'alerte "Training en cours"
   └─> État: pending/running

2. Clic sur "Arrêter et relancer"
   └─> Popup de confirmation: "Êtes-vous sûr ?"

3. Confirmation
   └─> API: POST /cancel
   └─> Celery: revoke(job_id, terminate=True)
   └─> DB: status = "cancelled"

4. Réinitialisation UI
   └─> runningJob = null
   └─> Bouton "Start Training" réactivé

5. Nouveau training possible
   └─> Utilisateur configure nouveau training
   └─> Clic "Start Training"
```

### Scénario 2 : Annulation Impossible
```
Status: "completed" ou "failed"
└─> Endpoint retourne: HTTP 400
└─> Message: "Cannot cancel job with status: completed"
```

## 🔒 Sécurité

### Validations Backend
- ✅ Authentification requise (JWT token)
- ✅ Vérification que le job appartient au projet
- ✅ Validation du statut (seulement pending/running)
- ✅ Protection contre les double-annulations

### Validations Frontend
- ✅ Confirmation utilisateur (popup)
- ✅ Désactivation du bouton pendant l'annulation
- ✅ Gestion des erreurs réseau
- ✅ Feedback visuel (loader, messages)

## 🐛 Gestion des Erreurs

### Backend
```python
try:
    celery_app.control.revoke(job_id, terminate=True)
except Exception as e:
    print(f"Warning: Could not revoke Celery task: {e}")
    # Continue quand même pour marquer le job comme annulé
```

### Frontend
```typescript
try {
  await cancelTraining();
  alert("Succès !");
} catch (error) {
  alert(error.response?.data?.detail || "Erreur générique");
}
```

## 📊 États des Jobs

### Nouveaux Statuts
- `"cancelled"` : Training annulé par l'utilisateur

### Transitions Autorisées
```
pending  ──(cancel)──> cancelled
running  ──(cancel)──> cancelled
completed ─────────────x (non autorisé)
failed   ──────────────x (non autorisé)
cancelled ─────────────x (non autorisé)
```

## 🧪 Tests

### Test Manuel
```bash
# 1. Lancer un training
curl -X POST http://localhost:8000/api/projects/1/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"epochs": 100, "batch_size": 16}'

# 2. Récupérer le job_id
JOB_ID="<id_retourné>"

# 3. Annuler le training
curl -X POST http://localhost:8000/api/projects/1/training/jobs/$JOB_ID/cancel \
  -H "Authorization: Bearer $TOKEN"

# 4. Vérifier le statut
curl http://localhost:8000/api/projects/1/training/jobs/$JOB_ID \
  -H "Authorization: Bearer $TOKEN"
# Résultat attendu: {"status": "cancelled", ...}
```

### Test Frontend
1. Se connecter à l'application
2. Aller sur `/projects/1/training`
3. Lancer un training (100 epochs)
4. Attendre que l'alerte apparaisse
5. Cliquer sur "Arrêter et relancer"
6. Confirmer l'annulation
7. Vérifier que le bouton "Start Training" se réactive
8. Lancer un nouveau training

## 📈 Améliorations Futures

### 1. Annulation Progressive (Graceful Shutdown)
```python
# Au lieu de SIGKILL, utiliser SIGTERM
celery_app.control.revoke(job_id, terminate=True, signal='SIGTERM')

# Permettre au training de sauvegarder l'état actuel
# Enregistrer le checkpoint du modèle à l'epoch actuelle
```

### 2. Reprise de Training
```python
# Option pour reprendre un training annulé
@router.post("/api/projects/{project_id}/training/jobs/{job_id}/resume")
async def resume_training_job(...):
    # Charger le dernier checkpoint
    # Relancer le training depuis l'epoch sauvegardée
```

### 3. Historique d'Annulations
```python
# Ajouter un champ dans TrainingJob
cancelled_by = Column(UUID, ForeignKey("users.id"))
cancelled_reason = Column(String)
```

### 4. Notifications
```python
# Notifier l'utilisateur par email/webhook
send_notification(
    user=job.project.owner,
    message=f"Training {job.id} cancelled at epoch {job.current_epoch}"
)
```

## 🎯 Impact

### Expérience Utilisateur
- ✅ Plus de flexibilité pour expérimenter
- ✅ Pas besoin d'attendre la fin d'un training incorrect
- ✅ Économie de ressources computationnelles
- ✅ Feedback immédiat

### Performance
- ✅ Libération immédiate des ressources GPU/CPU
- ✅ Nettoyage automatique des tâches Celery
- ✅ Pas de jobs "zombie" en base

## 📚 Références

- Celery revoke: https://docs.celeryproject.org/en/stable/userguide/workers.html#revoke
- YOLOv8 interruption: Géré par le signal system
- FastAPI background tasks: Délégation à Celery

## ✅ Checklist de Déploiement

- [x] Endpoint backend créé et testé
- [x] Frontend mis à jour avec bouton
- [x] Backend redémarré
- [x] Documentation créée
- [ ] Tests manuels effectués
- [ ] Validation en environnement de production
