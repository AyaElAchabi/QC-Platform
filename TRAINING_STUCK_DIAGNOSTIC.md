# 🔍 Diagnostic : Entraînement Bloqué

**Date**: 13 novembre 2025  
**Job ID**: cc85f1ad-1f41-488c-a9d4-8e8681c00233

## 📊 Symptômes

- ❌ Entraînement bloqué à l'epoch 3/10 (0.3% de progression)
- ⏱️ Job "running" depuis plus de 6 heures (12:46 → 19:39)
- 📉 Aucune nouvelle métrique générée
- 🔄 Worker Celery sans tâche active

## 🔎 Analyse

### État du Job en Base de Données
```
Status: running
Progress: 0.3%
Epoch: 3/10
Métriques: 9 enregistrées
Démarré il y a: 413.3 minutes (~7 heures)
```

### État du Worker Celery
```bash
$ celery -A workers.celery_app inspect active
→ celery@9bdf586f3f4d: OK
   - empty -
```

**🚨 Problème identifié** : Le job est marqué "running" en base mais aucune tâche n'est active dans Celery.

## 🔧 Cause Probable

1. **Crash silencieux du processus de training** : Le worker a planté sans mettre à jour le statut
2. **Perte de connexion** : Déconnexion entre le worker et la base de données
3. **Timeout** : Le training a pris trop de temps et le processus a été tué
4. **Problème mémoire** : OOM (Out Of Memory) du container

## ✅ Solution Appliquée

### 1. Nettoyage du Job Bloqué
```python
job.status = 'failed'
job.error_message = 'Job bloqué après 6h+ - redémarrage nécessaire'
job.completed_at = datetime.utcnow()
```

### 2. Redémarrage du Worker
```bash
docker-compose restart celery_worker
```

### 3. Vérification
```bash
docker logs mlops_celery_worker --tail 20
# Résultat: celery@9bdf586f3f4d ready. ✅
```

## 🛡️ Prévention Future

### 1. Ajouter un Timeout sur les Tâches Celery

**Fichier**: `backend/workers/celery_app.py`

```python
app.conf.update(
    task_time_limit=7200,  # 2 heures max
    task_soft_time_limit=6900,  # Warning après 1h55
)
```

### 2. Ajouter un Health Check

**Fichier**: `backend/workers/tasks.py`

```python
@app.task(bind=True)
def train_yolo_model(self, job_id: str, project_id: int):
    try:
        # ...code existant...
        
        # Health check toutes les 5 minutes
        last_update = time.time()
        
        def on_epoch_end(metrics):
            nonlocal last_update
            last_update = time.time()
            # ...update metrics...
        
        # Vérifier si le job est encore actif
        if time.time() - last_update > 600:  # 10 min sans update
            raise Exception("Training stuck - no updates for 10 minutes")
            
    except Exception as e:
        # Mark as failed
```

### 3. Surveillance Automatique

Créer un script de monitoring qui vérifie les jobs bloqués :

```python
# scripts/monitor_stuck_jobs.py
from datetime import datetime, timedelta

# Trouver les jobs "running" depuis > 2h
stuck_jobs = db.query(TrainingJob).filter(
    TrainingJob.status == 'running',
    TrainingJob.started_at < datetime.utcnow() - timedelta(hours=2)
).all()

for job in stuck_jobs:
    # Vérifier si la tâche existe dans Celery
    # Si non, marquer comme failed
```

### 4. Améliorer la Configuration Docker

**Fichier**: `docker-compose.yml`

```yaml
celery_worker:
  deploy:
    resources:
      limits:
        memory: 4G  # Augmenter la limite mémoire
      reservations:
        memory: 2G
  healthcheck:
    test: ["CMD", "celery", "-A", "workers.celery_app", "inspect", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## 📝 Prochaines Étapes

1. ✅ Worker redémarré et opérationnel
2. 🔄 Lancer un nouveau training pour tester
3. 📊 Surveiller les logs en temps réel
4. ⚙️ Implémenter les protections (timeout, health checks)

## 🧪 Test Recommandé

```bash
# 1. Lancer un nouveau training (via frontend ou API)
# 2. Surveiller les logs
docker logs -f mlops_celery_worker

# 3. Vérifier que les métriques s'accumulent
# 4. Confirmer que le training se termine normalement
```

## 📚 Références

- Job ID bloqué: `cc85f1ad-1f41-488c-a9d4-8e8681c00233`
- Durée avant échec: 413 minutes (~7h)
- Métriques enregistrées: 9 (epoch 0-3 partiellement)
- Action: Marqué "failed" + worker redémarré
