#!/bin/bash

# Script complet de vérification du système d'authentification
# Ce script vérifie et itère sur tous les aspects du système auth

set -e

echo "======================================"
echo "Vérification du Système d'Authentification"
echo "======================================"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Fonction pour afficher les étapes
print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Vérification des services Docker
print_step "1. Vérification des services Docker..."
if docker ps | grep -q "mlops_postgres"; then
    print_success "PostgreSQL est en cours d'exécution"
else
    print_error "PostgreSQL n'est pas démarré"
    echo "Démarrage de PostgreSQL..."
    docker-compose up -d postgres
    sleep 5
fi

if docker ps | grep -q "mlops_redis"; then
    print_success "Redis est en cours d'exécution"
else
    print_error "Redis n'est pas démarré"
    echo "Démarrage de Redis..."
    docker-compose up -d redis
    sleep 3
fi

if docker ps | grep -q "mlops_backend"; then
    print_success "Backend est en cours d'exécution"
else
    print_error "Backend n'est pas démarré"
    echo "Démarrage du Backend..."
    docker-compose up -d backend
    sleep 10
fi

echo ""

# 2. Vérification de la connectivité backend
print_step "2. Vérification de la connectivité backend..."
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" | grep -q "200"; then
    print_success "Backend répond correctement"
else
    print_error "Backend ne répond pas"
    echo "Vérification des logs..."
    docker-compose logs backend | tail -20
fi

echo ""

# 3. Vérification de la base de données
print_step "3. Vérification de la structure de la base de données..."
docker exec mlops_postgres psql -U admin -d mlops_qc -c "\d users" 2>&1 | grep -q "role" && \
    print_success "Table users contient la colonne role" || \
    print_error "Colonne role manquante - migration nécessaire"

echo ""

# 4. Vérification des utilisateurs de test
print_step "4. Vérification des utilisateurs de test..."
USER_COUNT=$(docker exec mlops_postgres psql -U admin -d mlops_qc -t -c "SELECT COUNT(*) FROM users;" | xargs)
echo "Nombre d'utilisateurs dans la base: $USER_COUNT"

if [ "$USER_COUNT" -lt 4 ]; then
    print_error "Utilisateurs de test manquants - création..."
    python3 backend/create_test_users.py
else
    print_success "Utilisateurs de test présents"
fi

# Affichage des utilisateurs
echo ""
echo "Utilisateurs actuels:"
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT id, username, email, role, is_active FROM users;" 2>&1 | head -20

echo ""

# 5. Test d'authentification
print_step "5. Test d'authentification pour chaque rôle..."

declare -a USERS=("admin" "chef" "operator" "viewer")
declare -a PASSWORDS=("Admin@2024" "Chef@2024" "Operator@2024" "Viewer@2024")

for i in "${!USERS[@]}"; do
    username="${USERS[$i]}"
    password="${PASSWORDS[$i]}"
    
    echo ""
    echo "Test de connexion: $username"
    
    # Tentative de connexion
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$username&password=$password")
    
    if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
        TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
        ROLE=$(echo "$RESPONSE" | jq -r '.role // "unknown"')
        print_success "Connexion réussie - Rôle: $ROLE"
        
        # Test d'accès aux utilisateurs (seulement pour admin)
        if [ "$username" = "admin" ]; then
            echo "  Test d'accès à la gestion des utilisateurs..."
            USERS_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/users" \
                -H "Authorization: Bearer $TOKEN")
            
            if echo "$USERS_RESPONSE" | jq -e '.' > /dev/null 2>&1; then
                USER_COUNT=$(echo "$USERS_RESPONSE" | jq 'length')
                print_success "Accès autorisé - $USER_COUNT utilisateurs retournés"
            else
                print_error "Erreur lors de l'accès aux utilisateurs"
            fi
        fi
    else
        print_error "Échec de connexion - Réponse: $RESPONSE"
    fi
done

echo ""

# 6. Vérification du frontend
print_step "6. Vérification du frontend..."
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200"; then
    print_success "Frontend accessible"
else
    print_error "Frontend non accessible"
    echo "Vérifiez si le serveur Next.js est démarré avec: cd frontend && npm run dev"
fi

echo ""

# 7. Vérification des fichiers clés
print_step "7. Vérification des fichiers clés du système d'authentification..."

declare -a REQUIRED_FILES=(
    "backend/models/roles.py"
    "backend/models/user.py"
    "backend/api/dependencies.py"
    "backend/api/routes/user_management.py"
    "frontend/src/types/roles.ts"
    "frontend/src/types/auth.ts"
    "frontend/src/lib/hooks/useAuth.tsx"
    "frontend/src/components/layout/Sidebar.tsx"
    "frontend/src/app/(app)/settings/users/page.tsx"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file"
    else
        print_error "$file manquant"
    fi
done

echo ""

# 8. Résumé et recommandations
print_step "8. Résumé et Recommandations"
echo ""
echo "======================================"
echo "IDENTIFIANTS DE TEST"
echo "======================================"
echo "Admin:    admin / Admin@2024"
echo "Chef:     chef / Chef@2024"
echo "Operator: operator / Operator@2024"
echo "Viewer:   viewer / Viewer@2024"
echo ""
echo "======================================"
echo "URLS"
echo "======================================"
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "API Docs: $BACKEND_URL/docs"
echo ""
echo "======================================"
echo "PROCHAINES ÉTAPES"
echo "======================================"
echo "1. Tester la connexion sur l'interface web ($FRONTEND_URL)"
echo "2. Vérifier la visibilité du menu 'Utilisateurs' pour admin"
echo "3. Tester les restrictions d'accès pour chaque rôle"
echo "4. Vérifier la gestion des utilisateurs (ajout/modification/suppression)"
echo ""

# 9. Génération d'un rapport
print_step "9. Génération du rapport..."
REPORT_FILE="auth_verification_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "Rapport de Vérification du Système d'Authentification"
    echo "Généré le: $(date)"
    echo ""
    echo "=== État des Services ==="
    docker-compose ps
    echo ""
    echo "=== Utilisateurs dans la Base ==="
    docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT id, username, email, role, is_active, created_at FROM users;"
    echo ""
    echo "=== Logs Backend (dernières 50 lignes) ==="
    docker-compose logs backend | tail -50
} > "$REPORT_FILE"

print_success "Rapport généré: $REPORT_FILE"
echo ""

echo "======================================"
echo "Vérification Terminée!"
echo "======================================"
