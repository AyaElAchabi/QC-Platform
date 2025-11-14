#!/bin/bash
set -e

echo "🗄️  Migration de la base de données..."
echo ""

# Vérifier que PostgreSQL est démarré
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ PostgreSQL n'est pas démarré. Lancez d'abord: docker-compose up -d postgres"
    exit 1
fi

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
sleep 5

# Exécuter les migrations
echo "🔄 Exécution des migrations Alembic..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "✅ Migrations terminées avec succès!"
echo ""

# Afficher la version actuelle
echo "📌 Version actuelle de la base de données:"
docker-compose exec -T backend alembic current

echo ""
echo "📊 Tables créées:"
docker-compose exec -T postgres psql -U admin -d mlops_qc -c "\dt"
