# 🚨 DIAGNOSTIC: Training Bloqué en "Pending"

**Date**: 13 novembre 2025, 20:10 UTC  
**Job ID**: `167a6e77-70c7-4dfa-a86a-0e732778c8e9`  
**Problème**: Training reste en statut "pending" et ne démarre jamais

## 📊 État Actuel

### Job de Training
```json
{
  "id": "167a6e77-70c7-4dfa-a86a-0e732778c8e9",
  "status": "pending",
  "progress": 0.0,
  "current_epoch": 0,
  "total_epochs": 10,
  "metrics": [],
  "started_at": null,
  "created_at": "2025-11-13T19:57:17"
}
```

**Durée en pending**: > 10 minutes  
**Métriques enregistrées**: 0  
**Worker activity**: Aucune

### Worker Celery
```bash
$ celery -A workers.celery_app inspect active
→ celery@9bdf586f3f4d: OK
   - empty -
```

**État**: ✅ En ligne, mais AUCUNE tâche active/réservée

## 🔍 Analyse

### 1. Le Job Est Créé en Base ✅
- Le job existe dans PostgreSQL
- Statut: "pending"
- Configuration valide

### 2. La Tâche N'Est PAS Envoyée à Celery ❌
- Aucun log dans le worker
- `inspect active` retourne vide
- `inspect reserved` retourne vide

### 3. Problème Probable: Configuration Celery

Le backend essaie d'envoyer la tâche mais elle n'arrive pas au worker.

**Causes possibles**:
1. ❌ Broker (RabbitMQ) non partagé entre backend et worker
2. ❌ Queue name différente
3. ❌ Import Celery incorrect dans le backend
4. ❌ Backend ne peut pas se connecter à RabbitMQ

## 🔧 Solution

### Diagnostic du Problème

#### Test 1: Vérifier la Connexion RabbitMQ
```bash
docker exec mlops_backend python3 << 'EOF'
from workers.celery_app import celery_app
print(f"Broker: {celery_app.conf.broker_url}")
print(f"Backend: {celery_app.conf.result_backend}")
EOF
```

#### Test 2: Vérifier que le Worker Écoute la Bonne Queue
```bash
docker logs mlops_celery_worker | grep "queue"
# Résultat attendu: .> training exchange=training(direct) key=training
```

#### Test 3: Envoyer une Tâche de Test
```python
from workers.tasks import train_yolo_model
result = train_yolo_model.delay("test-job-id")
print(f"Task sent: {result.id}")
```

### Fix Probable: Redémarrer Backend ET Worker

Le backend utilise une ancienne instance de Celery app en mémoire.

```bash
docker-compose restart backend celery_worker
```

### Si Ça Ne Marche Pas: Vérifier docker-compose.yml

**Backend doit avoir**:
```yaml
backend:
  environment:
    - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
```

**Worker doit avoir**:
```yaml
celery_worker:
  environment:
    - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
  command: celery -A workers.celery_app worker --loglevel=info -Q training
```

## 🎯 Action Immédiate

### Étape 1: Redémarrer les Services
```bash
cd /Users/mac/mlops-qc-platform
docker-compose restart backend celery_worker
```

### Étape 2: Surveiller les Logs
```bash
# Terminal 1
docker logs -f mlops_backend

# Terminal 2  
docker logs -f mlops_celery_worker
```

### Étape 3: Relancer le Training depuis le Frontend
1. Aller sur la page de training
2. Cliquer "Start Training"
3. Observer les logs en temps réel

### Étape 4: Vérifier que la Tâche Est Reçue
```bash
docker exec mlops_celery_worker celery -A workers.celery_app inspect active
# Devrait montrer la tâche en cours
```

## 📝 Checklist de Vérification

- [ ] Backend connecté à RabbitMQ
- [ ] Worker connecté à RabbitMQ  
- [ ] Worker écoute la queue "training"
- [ ] Job créé en base de données
- [ ] Tâche envoyée à RabbitMQ
- [ ] Worker reçoit la tâche
- [ ] Worker exécute la tâche
- [ ] Métriques commencent à s'enregistrer

## 🚀 Prochaine Étape

**REDÉMARRAGE COMPLET** recommandé pour synchroniser backend/worker/rabbitmq.
