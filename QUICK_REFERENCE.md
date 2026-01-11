# 🚀 GUIDE RAPIDE - Système d'Authentification

## Accès rapide

### 🌐 URLs
- **API Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **Gestion Users:** http://localhost:3000/settings/users

### 👤 Compte Admin Principal
```
Email: eyaelachabi@gmail.com
Mot de passe: Eyaelach0200@
Rôle: ADMIN (tous les droits)
```

### 🧪 Comptes de Test
```
admin@test.com / test123 (ADMIN)
chef@test.com / test123 (CHEF_OPERATOR)
operator@test.com / test123 (OPERATOR)
viewer@test.com / test123 (VIEWER)
```

## 📝 Commandes Utiles

### Test Complet
```bash
./test-users-complete.sh
```

### Connexion API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eyaelachabi@gmail.com","password":"Eyaelach0200@"}'
```

### Liste des Utilisateurs
```bash
TOKEN="YOUR_TOKEN_HERE"
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"
```

### Mes Permissions
```bash
TOKEN="YOUR_TOKEN_HERE"
curl http://localhost:8000/api/users/me/permissions \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Rôles et Permissions

### ADMIN (32 permissions)
✅ Tout peut faire

### CHEF_OPERATOR (28 permissions)
✅ Gérer équipe + opérations
❌ Pas de suppression système

### OPERATOR (14 permissions)
✅ Opérations quotidiennes
❌ Pas de gestion utilisateurs

### VIEWER (8 permissions)
✅ Lecture seule
❌ Pas de modifications

## 📋 Checklist Démarrage

- [x] Backend démarré (port 8000)
- [x] Frontend démarré (port 3000)
- [x] Base de données accessible
- [x] Migration appliquée
- [x] Compte admin créé
- [x] Tests API passants
- [x] Interface accessible

## 🔍 Vérifications Rapides

### Backend
```bash
docker ps | grep mlops_backend
curl http://localhost:8000/health
```

### Frontend
```bash
lsof -ti:3000
curl http://localhost:3000
```

### Database
```bash
docker exec -it mlops_postgres psql -U mlops_user -d mlops_qc \
  -c "SELECT email, role FROM users;"
```

## 📚 Documentation

- **Guide complet:** `AUTH_README.md`
- **Démarrage rapide:** `QUICK_START_AUTH.md`
- **Rapport final:** `FINAL_SUCCESS_REPORT.md`
- **Changelog:** `CHANGELOG_AUTH.md`

## ✅ Tout fonctionne!

Le système est opérationnel et prêt à l'emploi.
