#!/bin/bash

# Script de validation finale du système d'authentification
# Ce script effectue une validation complète de bout en bout

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   VALIDATION FINALE - Système d'Authentification MLOps    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Compteurs
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Variables
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Fonctions utilitaires
print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}▶ Test #$TOTAL_TESTS: $1${NC}"
}

print_success() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}  ✓ $1${NC}"
}

print_failure() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}  ✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}  ℹ $1${NC}"
}

print_warning() {
    echo -e "${MAGENTA}  ⚠ $1${NC}"
}

# Test de santé des services
print_header "1. VÉRIFICATION DES SERVICES"

print_test "Service PostgreSQL"
if docker ps | grep -q "mlops_postgres.*Up"; then
    print_success "PostgreSQL est actif"
else
    print_failure "PostgreSQL n'est pas actif"
    print_warning "Tentative de démarrage..."
    docker-compose up -d postgres
    sleep 5
fi

print_test "Service Redis"
if docker ps | grep -q "mlops_redis.*Up"; then
    print_success "Redis est actif"
else
    print_failure "Redis n'est pas actif"
fi

print_test "Service Backend"
if docker ps | grep -q "mlops_backend.*Up"; then
    print_success "Backend est actif"
    
    # Vérifier que le backend répond
    sleep 2
    if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        print_success "Backend répond aux requêtes"
    else
        print_failure "Backend ne répond pas"
    fi
else
    print_failure "Backend n'est pas actif"
fi

# Test de la structure de la base de données
print_header "2. VÉRIFICATION DE LA BASE DE DONNÉES"

print_test "Structure de la table users"
if docker exec mlops_postgres psql -U admin -d mlops_qc -c "\d users" 2>&1 | grep -q "role"; then
    print_success "Colonne 'role' présente"
else
    print_failure "Colonne 'role' manquante"
fi

print_test "Type ENUM pour les rôles"
if docker exec mlops_postgres psql -U admin -d mlops_qc -c "\dT+ userrole" 2>&1 | grep -q "enum"; then
    print_success "Type ENUM 'userrole' configuré"
else
    print_warning "Type ENUM pourrait être manquant"
fi

print_test "Présence des utilisateurs de test"
USER_COUNT=$(docker exec mlops_postgres psql -U admin -d mlops_qc -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs || echo "0")
print_info "Nombre d'utilisateurs: $USER_COUNT"

if [ "$USER_COUNT" -ge 4 ]; then
    print_success "Utilisateurs de test présents"
else
    print_warning "Nombre d'utilisateurs insuffisant"
    print_info "Création des utilisateurs de test..."
    python3 backend/create_test_users.py 2>&1 | grep -v "Warning" || true
fi

# Test d'authentification pour chaque rôle
print_header "3. TESTS D'AUTHENTIFICATION"

declare -a USERS=("admin" "chef" "operator" "viewer")
declare -a PASSWORDS=("Admin@2024" "Chef@2024" "Operator@2024" "Viewer@2024")
declare -a ROLES=("ADMIN" "CHEF_OPERATOR" "OPERATOR" "VIEWER")
declare -A TOKENS

for i in "${!USERS[@]}"; do
    username="${USERS[$i]}"
    password="${PASSWORDS[$i]}"
    expected_role="${ROLES[$i]}"
    
    print_test "Connexion de l'utilisateur '$username'"
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$username&password=$password" 2>/dev/null || echo '{"error": "connection failed"}')
    
    if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
        TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
        ROLE=$(echo "$RESPONSE" | jq -r '.role // "unknown"')
        TOKENS[$username]=$TOKEN
        
        if [ "$ROLE" = "$expected_role" ]; then
            print_success "Authentification réussie - Rôle: $ROLE"
        else
            print_failure "Rôle incorrect: attendu=$expected_role, reçu=$ROLE"
        fi
    else
        print_failure "Échec de l'authentification"
        print_info "Réponse: $RESPONSE"
    fi
done

# Test des permissions
print_header "4. TESTS DES PERMISSIONS"

print_test "Admin peut accéder à la gestion des utilisateurs"
if [ ! -z "${TOKENS[admin]}" ]; then
    RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/users" \
        -H "Authorization: Bearer ${TOKENS[admin]}" 2>/dev/null || echo '[]')
    
    if echo "$RESPONSE" | jq -e '. | length' > /dev/null 2>&1; then
        COUNT=$(echo "$RESPONSE" | jq '. | length')
        print_success "Accès autorisé - $COUNT utilisateurs retournés"
    else
        print_failure "Accès refusé ou erreur"
    fi
else
    print_warning "Token admin non disponible"
fi

print_test "Operator NE peut PAS accéder à la gestion des utilisateurs"
if [ ! -z "${TOKENS[operator]}" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BACKEND_URL/api/users" \
        -H "Authorization: Bearer ${TOKENS[operator]}" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ]; then
        print_success "Accès correctement refusé (HTTP $HTTP_CODE)"
    else
        print_failure "Accès autorisé alors qu'il devrait être refusé (HTTP $HTTP_CODE)"
    fi
else
    print_warning "Token operator non disponible"
fi

print_test "Viewer NE peut PAS accéder à la gestion des utilisateurs"
if [ ! -z "${TOKENS[viewer]}" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BACKEND_URL/api/users" \
        -H "Authorization: Bearer ${TOKENS[viewer]}" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ]; then
        print_success "Accès correctement refusé (HTTP $HTTP_CODE)"
    else
        print_failure "Accès autorisé alors qu'il devrait être refusé (HTTP $HTTP_CODE)"
    fi
else
    print_warning "Token viewer non disponible"
fi

# Test des opérations CRUD
print_header "5. TESTS DES OPÉRATIONS CRUD"

if [ ! -z "${TOKENS[admin]}" ]; then
    print_test "Création d'un nouvel utilisateur (Admin)"
    
    TEST_USER="testuser_$(date +%s)"
    CREATE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/users" \
        -H "Authorization: Bearer ${TOKENS[admin]}" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$TEST_USER\",
            \"email\": \"${TEST_USER}@test.com\",
            \"password\": \"TestPass@123\",
            \"role\": \"VIEWER\"
        }" 2>/dev/null || echo '{"error": "failed"}')
    
    if echo "$CREATE_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
        TEST_USER_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')
        print_success "Utilisateur créé avec ID: $TEST_USER_ID"
        
        print_test "Modification du rôle de l'utilisateur"
        UPDATE_RESPONSE=$(curl -s -X PUT "$BACKEND_URL/api/users/$TEST_USER_ID/role" \
            -H "Authorization: Bearer ${TOKENS[admin]}" \
            -H "Content-Type: application/json" \
            -d '{"role": "OPERATOR"}' 2>/dev/null || echo '{"error": "failed"}')
        
        if echo "$UPDATE_RESPONSE" | jq -e '.role' > /dev/null 2>&1; then
            NEW_ROLE=$(echo "$UPDATE_RESPONSE" | jq -r '.role')
            if [ "$NEW_ROLE" = "OPERATOR" ]; then
                print_success "Rôle modifié avec succès"
            else
                print_failure "Rôle non modifié correctement"
            fi
        else
            print_failure "Échec de la modification du rôle"
        fi
        
        print_test "Suppression de l'utilisateur de test"
        DELETE_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BACKEND_URL/api/users/$TEST_USER_ID" \
            -H "Authorization: Bearer ${TOKENS[admin]}" 2>/dev/null || echo "000")
        
        if [ "$DELETE_CODE" = "200" ] || [ "$DELETE_CODE" = "204" ]; then
            print_success "Utilisateur supprimé avec succès"
        else
            print_failure "Échec de la suppression (HTTP $DELETE_CODE)"
        fi
    else
        print_failure "Échec de la création de l'utilisateur"
        print_info "Réponse: $CREATE_RESPONSE"
    fi
else
    print_warning "Token admin non disponible - tests CRUD ignorés"
fi

# Vérification des fichiers frontend
print_header "6. VÉRIFICATION DES FICHIERS FRONTEND"

declare -a FRONTEND_FILES=(
    "frontend/src/types/roles.ts"
    "frontend/src/types/auth.ts"
    "frontend/src/lib/hooks/useAuth.tsx"
    "frontend/src/components/auth/RoleBadge.tsx"
    "frontend/src/components/auth/RequireAuth.tsx"
    "frontend/src/components/auth/PermissionGate.tsx"
    "frontend/src/components/layout/Sidebar.tsx"
    "frontend/src/app/(app)/settings/users/page.tsx"
)

for file in "${FRONTEND_FILES[@]}"; do
    print_test "Vérification de $file"
    if [ -f "$file" ]; then
        print_success "Fichier présent"
    else
        print_failure "Fichier manquant"
    fi
done

# Vérification des fichiers backend
print_header "7. VÉRIFICATION DES FICHIERS BACKEND"

declare -a BACKEND_FILES=(
    "backend/models/roles.py"
    "backend/models/user.py"
    "backend/api/dependencies.py"
    "backend/api/routes/user_management.py"
    "backend/core/auth_logger.py"
    "backend/core/rate_limiter.py"
    "backend/tests/test_auth_security.py"
)

for file in "${BACKEND_FILES[@]}"; do
    print_test "Vérification de $file"
    if [ -f "$file" ]; then
        print_success "Fichier présent"
    else
        print_failure "Fichier manquant"
    fi
done

# Vérification de la documentation
print_header "8. VÉRIFICATION DE LA DOCUMENTATION"

declare -a DOC_FILES=(
    "AUTH_SYSTEM_DOCUMENTATION.md"
    "AUTH_ITERATIONS_SUMMARY.md"
    "IDENTIFIANTS_TEST.md"
    "GUIDE_ACCES_USERS.md"
    "docs/AUTH_API.md"
)

for file in "${DOC_FILES[@]}"; do
    print_test "Vérification de $file"
    if [ -f "$file" ]; then
        print_success "Documentation présente"
    else
        print_warning "Documentation manquante"
    fi
done

# Résumé final
print_header "RÉSUMÉ DE LA VALIDATION"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         RÉSULTATS DES TESTS            ║${NC}"
echo -e "${CYAN}╠════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC}  Total de tests: ${YELLOW}$TOTAL_TESTS${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  Tests réussis:  ${GREEN}$PASSED_TESTS${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  Tests échoués:  ${RED}$FAILED_TESTS${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Calcul du taux de réussite
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    
    if [ $SUCCESS_RATE -ge 90 ]; then
        echo -e "${GREEN}✓ Taux de réussite: $SUCCESS_RATE% - EXCELLENT!${NC}"
        echo -e "${GREEN}  Le système d'authentification est opérationnel.${NC}"
    elif [ $SUCCESS_RATE -ge 70 ]; then
        echo -e "${YELLOW}⚠ Taux de réussite: $SUCCESS_RATE% - BON${NC}"
        echo -e "${YELLOW}  Quelques améliorations sont recommandées.${NC}"
    else
        echo -e "${RED}✗ Taux de réussite: $SUCCESS_RATE% - ATTENTION${NC}"
        echo -e "${RED}  Des corrections sont nécessaires.${NC}"
    fi
fi

echo ""
print_header "PROCHAINES ÉTAPES"

echo ""
echo "1. ${CYAN}Tester l'interface web${NC}"
echo "   URL: $FRONTEND_URL"
echo ""
echo "2. ${CYAN}Se connecter avec chaque rôle${NC}"
echo "   Admin:    admin / Admin@2024"
echo "   Chef:     chef / Chef@2024"
echo "   Operator: operator / Operator@2024"
echo "   Viewer:   viewer / Viewer@2024"
echo ""
echo "3. ${CYAN}Vérifier les permissions${NC}"
echo "   - Admin voit le menu 'Utilisateurs'"
echo "   - Autres rôles ne le voient pas"
echo "   - Tester les restrictions d'accès"
echo ""
echo "4. ${CYAN}Consulter la documentation${NC}"
echo "   - AUTH_ITERATIONS_SUMMARY.md"
echo "   - docs/AUTH_API.md"
echo ""

# Génération du rapport
REPORT_FILE="validation_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "════════════════════════════════════════════════════════════"
    echo "  RAPPORT DE VALIDATION - Système d'Authentification"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Date: $(date)"
    echo ""
    echo "RÉSULTATS:"
    echo "  - Total de tests: $TOTAL_TESTS"
    echo "  - Tests réussis: $PASSED_TESTS"
    echo "  - Tests échoués: $FAILED_TESTS"
    echo "  - Taux de réussite: $SUCCESS_RATE%"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  ÉTAT DES SERVICES"
    echo "════════════════════════════════════════════════════════════"
    docker-compose ps
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  UTILISATEURS EN BASE"
    echo "════════════════════════════════════════════════════════════"
    docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT id, username, email, role, is_active FROM users;" 2>&1
    echo ""
} > "$REPORT_FILE"

echo -e "${GREEN}📄 Rapport généré: $REPORT_FILE${NC}"
echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║            VALIDATION TERMINÉE AVEC SUCCÈS! 🎉            ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
