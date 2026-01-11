# 🎯 GUIDE DE TEST - Système d'Authentification

## ✅ Configuration Terminée

### Compte Admin Configuré
- **Email:** eyaelachabi@gmail.com
- **Mot de passe:** Eyaelach0200@
- **Rôle:** ADMIN

### Migration Base de Données
✅ Migration appliquée avec succès
✅ Enum PostgreSQL créé avec 4 valeurs : ADMIN, CHEF_OPERATOR, OPERATOR, VIEWER
✅ Compte admin mis à jour

### Utilisateurs de Test Créés
1. **ADMIN:** eyaelachabi@gmail.com / Eyaelach0200@
2. **CHEF_OPERATOR:** chef@test.com / password123
3. **OPERATOR:** operator@test.com / password123  
4. **VIEWER:** viewer@test.com / password123

---

## 🚀 Pour Démarrer les Tests

### Étape 1 : Reconstruire le Backend (EN COURS)

```bash
cd /Users/mac/mlops-qc-platform
docker compose build backend
docker compose up -d backend
```

**Pourquoi ?** Les nouveaux fichiers `roles.py` et `user_management.py` doivent être intégrés dans l'image Docker.

### Étape 2 : Vérifier que le Backend est Prêt

```bash
# Attendre 10 secondes puis tester
sleep 10
curl http://localhost:8000/health
```

### Étape 3 : Tester l'Authentification

```bash
# Se connecter en tant qu'admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}' | jq

# Sauvegarder le token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}' | jq -r '.access_token')
```

### Étape 4 : Tester les Nouvelles Routes

```bash
# Mon profil
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq

# Mes permissions
curl -X GET "http://localhost:8000/api/users/me/permissions" \
  -H "Authorization: Bearer $TOKEN" | jq

# Liste des utilisateurs (Admin uniquement)
curl -X GET "http://localhost:8000/api/users" \
  -H "Authorization: Bearer $TOKEN" | jq

# Liste des rôles
curl -X GET "http://localhost:8000/api/users/roles" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 🎨 Tester le Frontend

### Étape 1 : Le Frontend est Déjà Démarré

Le frontend tourne sur http://localhost:3000

### Étape 2 : Se Connecter

1. Aller sur http://localhost:3000/auth/login
2. Se connecter avec :
   - **Email:** eyaelachabi@gmail.com
   - **Mot de passe:** Eyaelach0200@

### Étape 3 : Accéder à la Gestion des Utilisateurs

Après connexion, aller sur :
http://localhost:3000/settings/users

**Vous devriez voir :**
- ✅ Liste de tous les utilisateurs
- ✅ Badge coloré pour chaque rôle (Admin = Violet, Chef = Bleu, Operator = Vert, Viewer = Gris)
- ✅ Barre de recherche
- ✅ Filtre par rôle
- ✅ Boutons d'action (Changer rôle, Activer/Désactiver, Supprimer)

### Étape 4 : Tester les Fonctionnalités

1. **Rechercher un utilisateur** : Tapez "chef" dans la barre de recherche
2. **Filtrer par rôle** : Sélectionnez "Chef Opérateur" dans le filtre
3. **Changer un rôle** :
   - Cliquez sur "Rôle" pour un utilisateur
   - Sélectionnez un nouveau rôle
   - Confirmez
4. **Désactiver un utilisateur** :
   - Cliquez sur "Désactiver"
   - Vérifiez que le statut change

---

## 🔍 Vérifications Importantes

### Backend
- [ ] Backend démarré sans erreur
- [ ] Route `/health` répond 200 OK
- [ ] Login fonctionne avec eyaelachabi@gmail.com
- [ ] Route `/api/users/me` retourne votre profil
- [ ] Route `/api/users` retourne la liste (admin uniquement)
- [ ] Route `/api/users/roles` retourne 4 rôles

### Frontend  
- [ ] Page de login accessible
- [ ] Connexion réussie avec vos identifiants
- [ ] Redirection vers /dashboard après login
- [ ] Page `/settings/users` accessible (admin)
- [ ] Liste des utilisateurs s'affiche
- [ ] Badges de rôles colorés visibles
- [ ] Recherche fonctionne
- [ ] Filtrage par rôle fonctionne
- [ ] Changement de rôle fonctionne

---

## 🐛 Problèmes Connus et Solutions

### Problème : Routes `/api/users` retournent 404

**Cause :** Le backend n'a pas été reconstruit avec les nouveaux fichiers.

**Solution :**
```bash
cd /Users/mac/mlops-qc-platform
docker compose build backend
docker compose up -d backend
sleep 10
```

### Problème : "Module 'roles' not found"

**Cause :** Le fichier `models/roles.py` n'est pas dans l'image Docker.

**Solution :** Reconstruire l'image (voir ci-dessus).

### Problème : Frontend ne se connecte pas

**Cause :** Le token n'est pas sauvegardé correctement.

**Solution :**
1. Ouvrir la console du navigateur (F12)
2. Vérifier les logs
3. Vider le localStorage : `localStorage.clear()`
4. Se reconnecter

### Problème : 403 Forbidden sur /api/users

**Cause :** L'utilisateur n'est pas admin.

**Solution :** Se connecter avec eyaelachabi@gmail.com (rôle ADMIN).

---

## 📊 Ce Qui a Été Implémenté

### Backend ✅
- ✅ Enum `UserRole` avec 4 rôles
- ✅ Enum `Permission` avec 40+ permissions
- ✅ Matrice de permissions par rôle
- ✅ Décorateurs de sécurité (`require_role`, `require_permission`, etc.)
- ✅ 10 routes API de gestion des utilisateurs
- ✅ Migration PostgreSQL ENUM
- ✅ Compte admin configuré

### Frontend ✅
- ✅ Types synchronisés avec le backend
- ✅ Hook `useAuth` avec vérification des permissions
- ✅ Composant `RoleBadge` pour afficher les rôles
- ✅ Composant `RequireAuth` pour protéger les routes
- ✅ Composant `PermissionGate` pour l'affichage conditionnel
- ✅ Interface complète de gestion des utilisateurs
- ✅ Page `/settings/users` (admin uniquement)

### Documentation ✅
- ✅ Guide backend (`AUTH_SYSTEM_DOCUMENTATION.md`)
- ✅ Guide frontend (`FRONTEND_AUTH_DOCUMENTATION.md`)
- ✅ Guide de démarrage (`QUICK_START_AUTH.md`)
- ✅ Récapitulatif complet (`AUTH_IMPLEMENTATION_COMPLETE.md`)
- ✅ Ce guide de test

---

## 🎯 Prochaines Étapes

### Immédiat
1. ⏳ **Attendre que le rebuild du backend se termine**
2. ⏳ Redémarrer le backend
3. ⏳ Tester les routes API
4. ⏳ Tester l'interface frontend

### Court Terme
- [ ] Ajouter des tests automatisés (pytest + jest)
- [ ] Implémenter l'audit trail
- [ ] Ajouter des notifications pour les changements de rôle
- [ ] Dashboard de statistiques des utilisateurs

### Moyen Terme
- [ ] Permissions par projet
- [ ] Groupes et équipes
- [ ] Délégation de permissions temporaires
- [ ] API Keys avec permissions limitées

### Long Terme
- [ ] 2FA pour les comptes admin
- [ ] SSO (OAuth2/SAML)
- [ ] Rate limiting par rôle
- [ ] IP whitelisting

---

## 📞 Besoin d'Aide ?

### Vérifier l'État du Système

```bash
# État des conteneurs
docker ps

# Logs du backend
docker logs mlops_backend --tail 50

# Logs du frontend (dans son terminal)

# Test rapide complet
./test-auth-quick.sh
```

### Documentsà Consulter

1. `AUTH_README.md` - Vue d'ensemble
2. `QUICK_START_AUTH.md` - Guide pas-à-pas
3. `backend/AUTH_SYSTEM_DOCUMENTATION.md` - Documentation backend
4. `frontend/FRONTEND_AUTH_DOCUMENTATION.md` - Documentation frontend

---

**Status :** ⏳ En attente du rebuild du backend  
**Prochaine action :** Attendre la fin du build, redémarrer et tester

🎉 **Le système est presque prêt pour les tests !**
