# MLOps QC Platform - Contrôle Qualité Visuel avec IA Explicable

Plateforme SaaS pour l'inspection visuelle industrielle avec Deep Learning et XAI (Explainable AI).

## 🚀 Quick Start

### 1. Prérequis

- Docker & Docker Compose
- Python 3.10+
- Git

### 2. Installation
```bash
# Cloner le projet
git clone <repo-url>
cd mlops-qc-platform

# Copier le fichier d'environnement
cd backend
cp .env.example .env

# Éditer .env avec vos configurations
nano .env
```

### 3. Démarrage avec Docker
```bash
# Retour à la racine
cd ..

# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f backend
```

### 4. Initialisation de la base de données
```bash
# Rendre le script exécutable
chmod +x scripts/init_db.sh

# Exécuter les migrations
./scripts/init_db.sh

# Seed data (utilisateurs de test)
docker exec -it mlops_backend python scripts/seed_data.py
```

### 5. Accès aux services

- **API Backend** : http://localhost:8000
- **API Docs (Swagger)** : http://localhost:8000/docs
- **MinIO Console** : http://localhost:9001 (minioadmin / minioadmin)
- **RabbitMQ Management** : http://localhost:15672 (guest / guest)

## 📦 Architecture
```
mlops-qc-platform/
├── backend/           # FastAPI application
│   ├── api/          # Routes & endpoints
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── workers/      # Celery tasks
│   └── core/         # Configuration & clients
├── frontend/         # Next.js app (Phase 3)
├── ml/               # ML scripts (Phase 4)
├── docker/           # Dockerfiles
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## 🧪 Tests
```bash
# Tests unitaires
docker exec -it mlops_backend pytest

# Tests avec coverage
docker exec -it mlops_backend pytest --cov=backend --cov-report=html
```

## 📚 Documentation

- [Architecture détaillée](docs/ARCHITECTURE.md)
- [Guide API](docs/API.md)
- [Guide de déploiement](docs/DEPLOYMENT.md)

## 🔑 Credentials de test
```
Admin:
  Email: admin@mlops-qc.com
  Password: admin123

Operator:
  Email: operator@mlops-qc.com
  Password: operator123
```

## 🛠️ Commandes utiles
```bash
# Arrêter tous les services
docker-compose down

# Reconstruire les images
docker-compose build

# Voir les logs d'un service
docker-compose logs -f [service_name]

# Entrer dans un conteneur
docker exec -it mlops_backend bash

# Créer une nouvelle migration
docker exec -it mlops_backend alembic revision --autogenerate -m "Description"

# Appliquer les migrations
docker exec -it mlops_backend alembic upgrade head
```

## 📝 TODO - Phase 3 & 4

- [ ] Frontend Next.js (Makerkit)
- [ ] Canvas d'annotation
- [ ] Scripts ML (YOLOv8, XAI)
- [ ] Intégration MLflow & DVC
- [ ] Dashboard Grafana
- [ ] Tests E2E

## 👥 Contributeurs

- Sabah Lemlih
- Aya El Achabi

## 📄 License

MIT License