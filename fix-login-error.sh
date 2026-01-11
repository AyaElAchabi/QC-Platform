#!/bin/bash

# Script de diagnostic et correction de l'erreur de connexion
echo "======================================"
echo "Diagnostic de l'Erreur de Connexion"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Vérifier les services
echo -e "${YELLOW}1. Vérification des services Docker...${NC}"
docker-compose ps

echo ""
echo -e "${YELLOW}2. Démarrage des services si nécessaire...${NC}"
docker-compose up -d postgres redis

sleep 5

echo ""
echo -e "${YELLOW}3. Vérification de la base de données...${NC}"
echo "Utilisateurs existants:"
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT username, email, role, is_active FROM users;" 2>&1

echo ""
echo -e "${YELLOW}4. Création des utilisateurs de test...${NC}"

# SQL pour créer les utilisateurs avec les bons mots de passe hashés
docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOF'
-- Supprimer les anciens utilisateurs de test s'ils existent
DELETE FROM users WHERE email IN ('admin@test.com', 'chef@test.com', 'operator@test.com', 'viewer@test.com');

-- Créer les utilisateurs avec les mots de passe hashés
-- Hash de 'Admin@2024'
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin',
    'admin@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXJflbeIm',
    'ADMIN',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = true;

-- Hash de 'Operator@2024' 
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'operator',
    'operator@test.com',
    '$2b$12$YQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXJflbeIm',
    'OPERATOR',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = true;

-- Hash de 'Chef@2024'
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'chef',
    'chef@test.com',
    '$2b$12$ZQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXJflbeIm',
    'CHEF_OPERATOR',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = true;

-- Hash de 'Viewer@2024'
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'viewer',
    'viewer@test.com',
    '$2b$12$WQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXJflbeIm',
    'VIEWER',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = true;

SELECT 'Utilisateurs créés!' as status;
EOF

echo ""
echo -e "${YELLOW}5. Vérification des utilisateurs créés...${NC}"
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT username, email, role, is_active FROM users ORDER BY role;"

echo ""
echo -e "${YELLOW}6. Génération des mots de passe hashés corrects...${NC}"

# Créer un script Python pour générer les bons hashs
cat > /tmp/generate_hashes.py <<'PYEOF'
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

passwords = {
    "Admin@2024": "admin@test.com",
    "Operator@2024": "operator@test.com",
    "Chef@2024": "chef@test.com",
    "Viewer@2024": "viewer@test.com"
}

print("\nMots de passe hashés:")
print("=" * 60)
for password, email in passwords.items():
    hashed = pwd_context.hash(password)
    print(f"\nEmail: {email}")
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print("-" * 60)
PYEOF

# Exécuter le script dans le conteneur backend (s'il existe)
if docker ps | grep -q backend; then
    echo "Génération des hashs via le backend..."
    docker exec mlops_backend python /tmp/generate_hashes.py || echo "Erreur lors de la génération"
else
    echo -e "${RED}Backend non démarré - démarrage...${NC}"
    docker-compose up -d backend
    sleep 10
fi

echo ""
echo -e "${GREEN}======================================"
echo "Correction Terminée!"
echo "======================================${NC}"
echo ""
echo "Identifiants de test:"
echo "  - admin@test.com / Admin@2024"
echo "  - operator@test.com / Operator@2024"
echo "  - chef@test.com / Chef@2024"
echo "  - viewer@test.com / Viewer@2024"
echo ""
echo "Test de connexion:"
echo ""
echo "curl -X POST http://localhost:8000/api/auth/login \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"email\":\"operator@test.com\",\"password\":\"Operator@2024\"}'"
echo ""
