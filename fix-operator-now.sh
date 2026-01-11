#!/bin/bash

echo "=========================================="
echo "CORRECTION RAPIDE - Utilisateur Operator"
echo "=========================================="
echo ""

# 1. Démarrer PostgreSQL si nécessaire
echo "1. Démarrage de PostgreSQL..."
docker-compose up -d postgres 2>&1
sleep 3

# 2. Vérifier si l'utilisateur existe
echo ""
echo "2. Vérification de l'utilisateur operator..."
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT username, email, role FROM users WHERE email='operator@test.com';" 2>&1

# 3. Supprimer et recréer l'utilisateur avec le bon hash
echo ""
echo "3. Recréation de l'utilisateur operator avec le mot de passe correct..."

docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOSQL'
-- Supprimer l'ancien utilisateur
DELETE FROM users WHERE email = 'operator@test.com';

-- Créer le nouvel utilisateur avec le hash correct pour "Operator@2024"
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'operator',
    'operator@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm',
    'OPERATOR'::userrole,
    true,
    true,
    NOW(),
    NOW()
);

SELECT 'Utilisateur operator créé!' as status;
EOSQL

# 4. Vérifier la création
echo ""
echo "4. Vérification de l'utilisateur créé..."
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT username, email, role, is_active FROM users WHERE email='operator@test.com';"

# 5. Démarrer le backend si nécessaire
echo ""
echo "5. Démarrage du backend..."
docker-compose up -d backend 2>&1
sleep 5

# 6. Test de connexion
echo ""
echo "6. Test de connexion API..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"operator@test.com","password":"Operator@2024"}')

echo "Réponse de l'API:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "=========================================="
echo "IDENTIFIANTS:"
echo "Email: operator@test.com"
echo "Mot de passe: Operator@2024"
echo "=========================================="
echo ""
echo "Essayez maintenant de vous connecter sur http://localhost:3000/auth/login"
echo ""
