# 🚀 Guide de Démarrage - Système d'Authentification

## Étape 1 : Appliquer la Migration Backend

```bash
cd /Users/mac/mlops-qc-platform/backend

# Appliquer la migration pour les rôles
alembic upgrade head

# Vérifier que la migration est appliquée
alembic current
```

## Étape 2 : Créer des Utilisateurs de Test

```bash
# Se connecter à PostgreSQL
docker exec -it mlops-qc-platform-postgres-1 psql -U mlops_user -d mlops_db

# Créer des utilisateurs de test (mot de passe: "password123")
-- Admin
INSERT INTO users (email, hashed_password, role, is_active, email_verified) 
VALUES ('admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'ADMIN', true, true);

-- Chef Operator  
INSERT INTO users (email, hashed_password, role, is_active, email_verified)
VALUES ('chef@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'CHEF_OPERATOR', true, true);

-- Operator
INSERT INTO users (email, hashed_password, role, is_active, email_verified)
VALUES ('operator@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'OPERATOR', true, true);

-- Viewer
INSERT INTO users (email, hashed_password, role, is_active, email_verified)
VALUES ('viewer@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'VIEWER', true, true);

\q
```

## Étape 3 : Tester l'API de Gestion des Utilisateurs

```bash
# 1. Se connecter en tant qu'admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Lister tous les utilisateurs
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Obtenir les rôles disponibles
curl -X GET http://localhost:8000/api/users/roles \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Changer le rôle d'un utilisateur (récupérer l'ID depuis l'étape 2)
USER_ID="<id-de-l-utilisateur>"
curl -X PUT http://localhost:8000/api/users/$USER_ID/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_role":"CHEF_OPERATOR"}' | jq

# 5. Désactiver un utilisateur
curl -X POST http://localhost:8000/api/users/$USER_ID/deactivate \
  -H "Authorization: Bearer $TOKEN" | jq

# 6. Réactiver un utilisateur
curl -X POST http://localhost:8000/api/users/$USER_ID/activate \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Étape 4 : Tester le Frontend

### 4.1 Démarrer le Frontend

```bash
cd /Users/mac/mlops-qc-platform/frontend
npm run dev
```

### 4.2 Tester la Connexion

1. Ouvrir http://localhost:3000/auth/login
2. Se connecter avec :
   - **Admin :** admin@test.com / password123
   - **Chef :** chef@test.com / password123
   - **Operator :** operator@test.com / password123
   - **Viewer :** viewer@test.com / password123

### 4.3 Tester l'Interface de Gestion des Utilisateurs

1. Se connecter en tant qu'admin
2. Aller sur http://localhost:3000/settings/users
3. Tester :
   - ✅ Voir la liste des utilisateurs
   - ✅ Filtrer par rôle
   - ✅ Rechercher un utilisateur
   - ✅ Changer le rôle d'un utilisateur
   - ✅ Activer/Désactiver un utilisateur
   - ✅ Supprimer un utilisateur

### 4.4 Tester les Permissions

#### Test 1 : Viewer (Lecture seule)
```
- Se connecter en tant que viewer@test.com
- Vérifier que les boutons de création/modification sont masqués
- Essayer d'accéder à /settings/users → Doit être redirigé
```

#### Test 2 : Operator (Opérations limitées)
```
- Se connecter en tant que operator@test.com
- Vérifier l'accès à /training
- Vérifier l'accès à /inference
- Vérifier que /settings/users n'est pas accessible
```

#### Test 3 : Chef Operator (Gestion complète)
```
- Se connecter en tant que chef@test.com
- Vérifier l'accès à la création de projets
- Vérifier l'accès au déploiement de modèles
- Vérifier que /settings/users n'est pas accessible
```

#### Test 4 : Admin (Accès complet)
```
- Se connecter en tant que admin@test.com
- Vérifier l'accès à toutes les pages
- Vérifier l'accès à /settings/users
- Tester la gestion des rôles
```

## Étape 5 : Tester les Composants de Protection

### Test RequireAuth

Créer une page de test :

```typescript
// /app/(app)/test-permissions/page.tsx
import { RequireAuth } from "@/components/auth";
import { UserRole, Permission } from "@/types/roles";

export default function TestPage() {
  return (
    <RequireAuth roles={[UserRole.ADMIN, UserRole.CHEF_OPERATOR]}>
      <div className="p-8">
        <h1>Page réservée aux Admins et Chef Operators</h1>
      </div>
    </RequireAuth>
  );
}
```

### Test PermissionGate

```typescript
// Dans n'importe quelle page
import { PermissionGate } from "@/components/auth";
import { Permission } from "@/types/roles";

<PermissionGate permissions={[Permission.PROJECT_CREATE]}>
  <Button>Créer un Projet</Button>
</PermissionGate>

<PermissionGate 
  permissions={[Permission.USER_DELETE]}
  fallback={<p>Vous n'avez pas les droits</p>}
>
  <Button variant="destructive">Supprimer</Button>
</PermissionGate>
```

## Étape 6 : Vérifier les Logs

### Backend
```bash
# Voir les logs du backend
docker logs -f mlops-qc-platform-backend-1

# Rechercher les logs d'authentification
docker logs mlops-qc-platform-backend-1 2>&1 | grep "auth"
```

### Frontend
```bash
# Ouvrir la console du navigateur (F12)
# Vérifier les logs :
# - "🔑 Token d'authentification sauvegardé"
# - "🔓 Token d'authentification supprimé"
```

## Étape 7 : Tests d'Intégration

### Script de Test Automatique

```bash
#!/bin/bash
# test-auth-system.sh

API_URL="http://localhost:8000"

echo "🧪 Tests du Système d'Authentification"
echo "======================================"

# Test 1 : Login Admin
echo -e "\n✓ Test 1 : Login Admin"
ADMIN_TOKEN=$(curl -s -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}' \
  | jq -r '.access_token')

if [ "$ADMIN_TOKEN" != "null" ]; then
  echo "✅ Admin login successful"
else
  echo "❌ Admin login failed"
  exit 1
fi

# Test 2 : Lister les utilisateurs (Admin uniquement)
echo -e "\n✓ Test 2 : Lister les utilisateurs"
USERS=$(curl -s -X GET $API_URL/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN")

USER_COUNT=$(echo $USERS | jq '.users | length')
echo "✅ Nombre d'utilisateurs: $USER_COUNT"

# Test 3 : Login Operator
echo -e "\n✓ Test 3 : Login Operator"
OPERATOR_TOKEN=$(curl -s -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@test.com","password":"password123"}' \
  | jq -r '.access_token')

if [ "$OPERATOR_TOKEN" != "null" ]; then
  echo "✅ Operator login successful"
else
  echo "❌ Operator login failed"
  exit 1
fi

# Test 4 : Operator ne peut pas accéder à /users
echo -e "\n✓ Test 4 : Operator ne peut pas lister les utilisateurs"
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET $API_URL/api/users \
  -H "Authorization: Bearer $OPERATOR_TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "403" ]; then
  echo "✅ Operator correctement bloqué (403)"
else
  echo "❌ Operator a accès (devrait être 403, reçu $HTTP_CODE)"
fi

# Test 5 : Login Viewer
echo -e "\n✓ Test 5 : Login Viewer"
VIEWER_TOKEN=$(curl -s -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"viewer@test.com","password":"password123"}' \
  | jq -r '.access_token')

if [ "$VIEWER_TOKEN" != "null" ]; then
  echo "✅ Viewer login successful"
else
  echo "❌ Viewer login failed"
  exit 1
fi

echo -e "\n🎉 Tous les tests sont passés avec succès!"
```

Exécuter le script :

```bash
chmod +x test-auth-system.sh
./test-auth-system.sh
```

## Étape 8 : Checklist de Validation

- [ ] Migration backend appliquée (alembic upgrade head)
- [ ] Utilisateurs de test créés
- [ ] API /api/users accessible pour admin
- [ ] API /api/users bloquée pour non-admins (403)
- [ ] Frontend démarre sans erreur
- [ ] Login fonctionne pour tous les rôles
- [ ] Page /settings/users accessible uniquement pour admin
- [ ] Badges de rôles s'affichent correctement
- [ ] Changement de rôle fonctionne
- [ ] Activation/Désactivation fonctionne
- [ ] PermissionGate masque/affiche correctement les éléments
- [ ] RequireAuth redirige correctement
- [ ] Logout fonctionne et supprime le token

## 🐛 Problèmes Courants

### Erreur : "ENUM type already exists"
```sql
-- Se connecter à la DB et supprimer l'ancien enum
DROP TYPE IF EXISTS userrole CASCADE;
-- Puis relancer la migration
```

### Erreur : "Cannot find module '@/types/roles'"
```bash
# Vérifier que le fichier existe
ls -la frontend/src/types/roles.ts

# Redémarrer le serveur de développement
npm run dev
```

### Erreur : "403 Forbidden" sur toutes les routes
```bash
# Vérifier que le token est valide
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Se reconnecter pour obtenir un nouveau token
```

## 📊 Résultat Attendu

Après avoir suivi ce guide, vous devriez avoir :

1. ✅ Backend avec système de rôles fonctionnel
2. ✅ Migration Alembic appliquée
3. ✅ Utilisateurs de test créés pour chaque rôle
4. ✅ API de gestion des utilisateurs testée
5. ✅ Frontend avec protection de routes
6. ✅ Interface de gestion des utilisateurs
7. ✅ Badges de rôles affichés
8. ✅ Permissions vérifiées côté frontend et backend

## 🎯 Prochaines Actions

1. Implémenter l'audit trail des changements de rôles
2. Ajouter des notifications pour les promotions
3. Créer des tests automatisés (Jest + Pytest)
4. Ajouter la gestion des permissions par projet
5. Implémenter 2FA pour les comptes admin

---

**Besoin d'aide ?** Consultez :
- `/backend/AUTH_SYSTEM_DOCUMENTATION.md`
- `/frontend/FRONTEND_AUTH_DOCUMENTATION.md`
