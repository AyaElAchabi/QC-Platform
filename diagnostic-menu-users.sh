#!/bin/bash

echo "🔍 DIAGNOSTIC COMPLET - Menu Utilisateurs manquant"
echo "=================================================="
echo ""

echo "1️⃣ Vérification du fichier Sidebar.tsx..."
if grep -q "Utilisateurs" /Users/mac/mlops-qc-platform/frontend/src/components/layout/Sidebar.tsx; then
    echo "   ✅ Menu 'Utilisateurs' présent dans le code"
    grep -A 2 "title: \"Utilisateurs\"" /Users/mac/mlops-qc-platform/frontend/src/components/layout/Sidebar.tsx
else
    echo "   ❌ Menu 'Utilisateurs' ABSENT du code"
fi
echo ""

echo "2️⃣ Vérification du processus frontend..."
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend actif sur port 3000"
    echo "   PID: $(lsof -ti:3000)"
else
    echo "   ❌ Frontend NON actif sur port 3000"
fi
echo ""

echo "3️⃣ Test de l'API de connexion..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
if [ "$TOKEN" != "null" ] && [ ! -z "$TOKEN" ]; then
    echo "   ✅ Connexion API réussie"
    
    # Décoder le JWT
    PAYLOAD=$(echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null || echo $TOKEN | cut -d'.' -f2 | base64 -D 2>/dev/null)
    ROLE=$(echo $PAYLOAD | jq -r '.role' 2>/dev/null)
    EMAIL=$(echo $PAYLOAD | jq -r '.email' 2>/dev/null)
    
    echo "   Email JWT: $EMAIL"
    echo "   Rôle JWT: $ROLE"
else
    echo "   ❌ Échec de connexion API"
fi
echo ""

echo "4️⃣ Instructions de correction..."
echo "   Pour corriger le problème:"
echo ""
echo "   A. DÉCONNEXION"
echo "      1. Ouvrez http://localhost:3000"
echo "      2. Cliquez sur 'Déconnexion' en bas de la sidebar"
echo ""
echo "   B. NETTOYAGE"
echo "      3. Ouvrez la Console (F12)"
echo "      4. Dans l'onglet Console, tapez:"
echo "         localStorage.clear()"
echo "      5. Appuyez sur Entrée"
echo ""
echo "   C. RECONNEXION"
echo "      6. Allez sur http://localhost:3000/auth/login"
echo "      7. Connectez-vous avec:"
echo "         Email: eyaelachabi@gmail.com"
echo "         Password: Eyaelach0200@"
echo ""
echo "   D. VÉRIFICATION"
echo "      8. Dans la console, tapez:"
echo "         console.log(localStorage.getItem('mlops_user_role'))"
echo "      9. Vous devriez voir: 'ADMIN'"
echo "     10. Rechargez la page (F5)"
echo "     11. Le menu 'Utilisateurs' devrait apparaître !"
echo ""
echo "=================================================="
echo "✅ Diagnostic terminé"
echo ""
