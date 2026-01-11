#!/bin/bash

# Script pour créer/réinitialiser les mots de passe des utilisateurs de test

echo "🔐 Création des identifiants de test pour tous les rôles"
echo "========================================================"
echo ""

# Générer les hashs bcrypt pour le mot de passe "Test1234!"
# Mot de passe : Test1234!

echo "1️⃣ Connexion à la base de données..."

# Hasher le mot de passe avec Python
HASHED_PASSWORD=$(docker exec mlops_backend python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('Test1234!'))
")

echo "   ✅ Hash généré: ${HASHED_PASSWORD:0:20}..."
echo ""

echo "2️⃣ Mise à jour des mots de passe dans la base..."

# Mettre à jour les mots de passe pour chaque utilisateur de test
docker exec mlops_postgres psql -U mlops_user -d mlops_qc << EOF
-- Chef Opérateur
UPDATE users SET password_hash = '$HASHED_PASSWORD' WHERE email = 'chef@test.com';

-- Opérateur
UPDATE users SET password_hash = '$HASHED_PASSWORD' WHERE email = 'operator@test.com';

-- Visualiseur
UPDATE users SET password_hash = '$HASHED_PASSWORD' WHERE email = 'viewer@test.com';

-- Admin test
UPDATE users SET password_hash = '$HASHED_PASSWORD' WHERE email = 'admin@test.com';

-- Afficher les utilisateurs mis à jour
SELECT email, role, is_active FROM users WHERE email IN ('chef@test.com', 'operator@test.com', 'viewer@test.com', 'admin@test.com');
EOF

echo ""
echo "✅ Mots de passe mis à jour !"
echo ""
echo "========================================================"
echo "📋 IDENTIFIANTS DE CONNEXION"
echo "========================================================"
echo ""
echo "👑 ADMINISTRATEUR"
echo "   Email:    eyaelachabi@gmail.com"
echo "   Password: Eyaelach0200@"
echo "   Rôle:     ADMIN"
echo "   Accès:    TOUT (gestion utilisateurs, projets, modèles, etc.)"
echo ""
echo "👑 ADMINISTRATEUR (Test)"
echo "   Email:    admin@test.com"
echo "   Password: Test1234!"
echo "   Rôle:     ADMIN"
echo "   Accès:    TOUT"
echo ""
echo "👨‍💼 CHEF OPÉRATEUR"
echo "   Email:    chef@test.com"
echo "   Password: Test1234!"
echo "   Rôle:     CHEF_OPERATOR"
echo "   Accès:    Projets, Images, Modèles, Entraînements, Inférence"
echo "   Limites:  ❌ Pas de gestion utilisateurs"
echo ""
echo "👷 OPÉRATEUR"
echo "   Email:    operator@test.com"
echo "   Password: Test1234!"
echo "   Rôle:     OPERATOR"
echo "   Accès:    Upload images, Annotations, Inférence"
echo "   Limites:  ❌ Pas de création de projets, ❌ Pas d'entraînements"
echo ""
echo "👁️  VISUALISEUR"
echo "   Email:    viewer@test.com"
echo "   Password: Test1234!"
echo "   Rôle:     VIEWER"
echo "   Accès:    Lecture seule (projets, images, résultats)"
echo "   Limites:  ❌ Aucune modification possible"
echo ""
echo "========================================================"
echo ""
echo "🧪 POUR TESTER:"
echo "1. Déconnectez-vous de la plateforme"
echo "2. Allez sur http://localhost:3000/auth/login"
echo "3. Connectez-vous avec l'un des comptes ci-dessus"
echo "4. Observez les différences d'interface et d'accès"
echo ""
echo "✅ Prêt à tester !"
