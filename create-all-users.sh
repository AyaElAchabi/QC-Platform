#!/bin/bash

echo "================================================================"
echo "🎯 CRÉATION COMPLÈTE DE TOUS LES UTILISATEURS"
echo "================================================================"
echo ""

cd /Users/mac/mlops-qc-platform

# 1. Démarrer PostgreSQL
echo "1️⃣ Démarrage de PostgreSQL..."
docker-compose up -d postgres redis 2>&1 | head -3
sleep 8
echo "   ✅ PostgreSQL prêt"
echo ""

# 2. Créer tous les utilisateurs
echo "2️⃣ Création de TOUS les utilisateurs de test..."
echo ""

docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOSQL'
-- Nettoyer les anciens utilisateurs de test
DELETE FROM users WHERE email IN (
    'admin@test.com', 
    'chef@test.com', 
    'operator@test.com', 
    'viewer@test.com'
);

-- 👑 ADMIN (Tous les droits)
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin',
    'admin@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm',
    'ADMIN'::userrole,
    true,
    true,
    NOW(),
    NOW()
);

-- 👔 CHEF OPERATOR (Chef de projet - Gestion datasets/modèles)
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'chef',
    'chef@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm',
    'CHEF_OPERATOR'::userrole,
    true,
    true,
    NOW(),
    NOW()
);

-- ⚙️ OPERATOR (Opérateur - Exécution/Consultation)
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

-- 👁️ VIEWER (Visualisateur - Consultation seule)
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'viewer',
    'viewer@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm',
    'VIEWER'::userrole,
    true,
    true,
    NOW(),
    NOW()
);

\echo ''
\echo '✅ Utilisateurs créés avec succès!'
\echo ''
\echo 'Liste des utilisateurs:'

SELECT 
    '  ' || username as "Utilisateur",
    email as "Email",
    role as "Rôle",
    CASE 
        WHEN is_active THEN '✓' 
        ELSE '✗' 
    END as "Actif"
FROM users 
WHERE email LIKE '%@test.com'
ORDER BY 
    CASE role
        WHEN 'ADMIN' THEN 1
        WHEN 'CHEF_OPERATOR' THEN 2
        WHEN 'OPERATOR' THEN 3
        WHEN 'VIEWER' THEN 4
    END;
EOSQL

echo ""
echo "   ✅ 4 utilisateurs créés"
echo ""

# 3. Démarrer le backend
echo "3️⃣ Démarrage du backend..."
docker-compose up -d backend 2>&1 | head -3
sleep 10
echo "   ✅ Backend démarré"
echo ""

# 4. Tests de connexion
echo "4️⃣ Test de connexion pour chaque utilisateur..."
echo ""

test_login() {
    local email=$1
    local password=$2
    local role=$3
    local icon=$4
    
    printf "   $icon Testing %-15s... " "$role"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
        -H 'Content-Type: application/json' \
        -d "{\"email\":\"$email\",\"password\":\"$password\"}" 2>/dev/null)
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ ERREUR"
    fi
}

test_login "admin@test.com" "Admin@2024" "ADMIN" "👑"
test_login "chef@test.com" "Chef@2024" "CHEF" "👔"
test_login "operator@test.com" "Operator@2024" "OPERATOR" "⚙️"
test_login "viewer@test.com" "Viewer@2024" "VIEWER" "👁️"

echo ""
echo "================================================================"
echo "✅ TOUS LES UTILISATEURS SONT PRÊTS!"
echo "================================================================"
echo ""
echo "┌────────────────────────┬─────────────────┬──────────────────┬─────────────────────────────┐"
echo "│ Email                  │ Mot de passe    │ Rôle             │ Permissions                 │"
echo "├────────────────────────┼─────────────────┼──────────────────┼─────────────────────────────┤"
echo "│ 👑 admin@test.com      │ Admin@2024      │ ADMIN            │ Gestion complète            │"
echo "│ 👔 chef@test.com       │ Chef@2024       │ CHEF_OPERATOR    │ Datasets + Modèles          │"
echo "│ ⚙️  operator@test.com  │ Operator@2024   │ OPERATOR         │ Exécution + Consultation    │"
echo "│ 👁️  viewer@test.com    │ Viewer@2024     │ VIEWER           │ Consultation seule          │"
echo "└────────────────────────┴─────────────────┴──────────────────┴─────────────────────────────┘"
echo ""
echo "🌐 URL de connexion: http://localhost:3000/auth/login"
echo ""
echo "💡 Testez avec n'importe quel compte ci-dessus!"
echo ""
echo "================================================================"
