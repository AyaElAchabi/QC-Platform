#!/bin/bash

echo "🔍 Vérification de l'état du frontend"
echo "======================================"
echo ""

# Vérifier si le frontend est en cours d'exécution
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "✅ Frontend en cours d'exécution sur le port 3000"
    PID=$(lsof -ti:3000)
    echo "   PID: $PID"
else
    echo "❌ Frontend non démarré sur le port 3000"
    echo ""
    echo "Pour démarrer le frontend :"
    echo "   cd /Users/mac/mlops-qc-platform/frontend"
    echo "   npm run dev"
    exit 1
fi

echo ""
echo "🔄 Redémarrage du serveur de développement..."
echo "   (pour appliquer les changements)"
echo ""

# Tuer le processus actuel
kill -9 $(lsof -ti:3000) 2>/dev/null

sleep 2

echo "✅ Processus arrêté"
echo ""
echo "Pour redémarrer :"
echo "   cd /Users/mac/mlops-qc-platform/frontend"
echo "   npm run dev"
echo ""
echo "Puis testez :"
echo "   1. Ouvrir http://localhost:3000"
echo "   2. Vérifier la redirection vers /auth/login"
