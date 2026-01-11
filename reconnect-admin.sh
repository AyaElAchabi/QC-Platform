#!/bin/bash

echo "🔄 Reconnexion automatique pour charger le rôle..."
echo ""

# 1. Nettoyer le localStorage (via l'API)
echo "1️⃣ Nettoyage du cache..."

# 2. Se connecter
echo "2️⃣ Connexion admin..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
EMAIL=$(echo $RESPONSE | jq -r '.user.email')
ROLE=$(echo $RESPONSE | jq -r '.user.role')
USER_ID=$(echo $RESPONSE | jq -r '.user.id')

echo "   ✅ Token reçu: ${TOKEN:0:50}..."
echo "   ✅ Email: $EMAIL"
echo "   ✅ Rôle: $ROLE"
echo "   ✅ ID: $USER_ID"
echo ""

# 3. Instructions pour l'utilisateur
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║  ✅ CONNEXION RÉUSSIE                             ║"
echo "║                                                   ║"
echo "╠═══════════════════════════════════════════════════╣"
echo "║                                                   ║"
echo "║  📋 INSTRUCTIONS:                                 ║"
echo "║                                                   ║"
echo "║  1. Ouvrez http://localhost:3000/auth/login       ║"
echo "║                                                   ║"
echo "║  2. Connectez-vous avec:                          ║"
echo "║     Email:    eyaelachabi@gmail.com               ║"
echo "║     Password: Eyaelach0200@                       ║"
echo "║                                                   ║"
echo "║  3. Après connexion, regardez le menu à gauche    ║"
echo "║                                                   ║"
echo "║  4. Vous DEVRIEZ voir:                            ║"
echo "║     👥 Utilisateurs                               ║"
echo "║                                                   ║"
echo "║  5. Cliquez dessus pour accéder à la gestion      ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

echo "💡 Si vous ne voyez TOUJOURS PAS le menu:"
echo "   → Ouvrez la Console du navigateur (F12)"
echo "   → Regardez les logs 'Sidebar - Role'"
echo "   → Envoyez-moi une capture d'écran"
echo ""
