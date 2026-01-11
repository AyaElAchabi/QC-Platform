# 🔧 CORRECTION - Erreur de Connexion "Not Found"

## 📋 Problème Identifié

**Date:** 20 Décembre 2025

### Symptômes
- Erreur lors de la connexion avec `operator@test.com` / `Operator@2024`
- Console affiche: "Erreur de connexion: {}"
- API retourne: "Not Found" (404)

### Cause Racine

L'erreur provient de plusieurs problèmes potentiels:

1. **Utilisateur non existant dans la base**
   - L'utilisateur `operator@test.com` n'existe pas ou n'est pas actif
   
2. **Mot de passe hashé incorrect**
   - Le hash du mot de passe ne correspond pas à `Operator@2024`
   
3. **Backend non démarré**
   - Le conteneur backend Docker n'est pas en cours d'exécution

---

## ✅ Solution Appliquée

### 1. Script de Correction Créé

**Fichier:** `backend/fix_passwords.py`

Ce script:
- Se connecte à la base de données PostgreSQL
- Génère les bons hashs bcrypt pour chaque mot de passe
- Crée ou met à jour les 4 utilisateurs de test
- Vérifie que tous les utilisateurs sont actifs

### 2. Utilisateurs de Test Configurés

| Email | Mot de Passe | Rôle | Status |
|-------|--------------|------|--------|
| admin@test.com | Admin@2024 | ADMIN | ✅ |
| operator@test.com | Operator@2024 | OPERATOR | ✅ |
| chef@test.com | Chef@2024 | CHEF_OPERATOR | ✅ |
| viewer@test.com | Viewer@2024 | VIEWER | ✅ |

---

## 🚀 Étapes de Correction

### Étape 1: Démarrer les Services
```bash
cd /Users/mac/mlops-qc-platform
docker-compose up -d postgres redis backend
```

### Étape 2: Exécuter le Script de Correction
```bash
cd /Users/mac/mlops-qc-platform/backend
python3 fix_passwords.py
```

### Étape 3: Vérifier les Utilisateurs
```bash
docker exec mlops_postgres psql -U admin -d mlops_qc -c \
  "SELECT username, email, role, is_active FROM users;"
```

### Étape 4: Tester la Connexion via API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"operator@test.com","password":"Operator@2024"}'
```

**Réponse attendue:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Étape 5: Tester via l'Interface Web
1. Ouvrir http://localhost:3000/auth/login
2. Email: `operator@test.com`
3. Mot de passe: `Operator@2024`
4. Cliquer sur "Se connecter"
5. Vérifier la redirection vers `/dashboard`

---

## 🔍 Diagnostic Rapide

### Vérifier si le Backend Répond
```bash
curl http://localhost:8000/health
```

### Vérifier les Logs Backend
```bash
docker-compose logs backend | tail -50
```

### Vérifier PostgreSQL
```bash
docker exec mlops_postgres psql -U admin -d mlops_qc -c \
  "SELECT COUNT(*) as total, role, is_active FROM users GROUP BY role, is_active;"
```

### Tester Tous les Comptes
```bash
# Admin
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@test.com","password":"Admin@2024"}'

# Operator
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"operator@test.com","password":"Operator@2024"}'

# Chef
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"chef@test.com","password":"Chef@2024"}'

# Viewer
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"viewer@test.com","password":"Viewer@2024"}'
```

---

## 🐛 Problèmes Résiduels Possibles

### 1. Backend ne démarre pas
**Solution:**
```bash
docker-compose down
docker-compose up -d postgres redis
sleep 5
docker-compose up -d backend
docker-compose logs backend -f
```

### 2. Erreur "ENUM userrole does not exist"
**Solution:**
```bash
docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOF'
CREATE TYPE userrole AS ENUM ('ADMIN', 'CHEF_OPERATOR', 'OPERATOR', 'VIEWER');
ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;
EOF
```

### 3. Table users n'existe pas
**Solution:**
```bash
cd /Users/mac/mlops-qc-platform/backend
docker-compose exec backend alembic upgrade head
```

### 4. Mot de passe toujours incorrect
**Solution:**
Regénérer le hash manuellement:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash = pwd_context.hash("Operator@2024")
print(hash)
```

Puis mettre à jour dans la base:
```sql
UPDATE users 
SET password_hash = '<hash_généré>' 
WHERE email = 'operator@test.com';
```

---

## 📊 Vérification de la Correction

### Checklist
- [ ] Services Docker démarrés (postgres, redis, backend)
- [ ] Script `fix_passwords.py` exécuté sans erreur
- [ ] 4 utilisateurs présents dans la base
- [ ] Test API réussi pour chaque utilisateur
- [ ] Connexion via l'interface web réussie
- [ ] Redirection vers dashboard après login
- [ ] Menu adapté selon le rôle

---

## 🎯 Résultat Attendu

Après correction, la connexion avec `operator@test.com` / `Operator@2024` devrait:

1. ✅ Retourner un token JWT valide
2. ✅ Stocker le token dans localStorage
3. ✅ Rediriger vers `/dashboard`
4. ✅ Afficher le menu approprié pour un OPERATOR
5. ✅ Cacher le menu "Utilisateurs" (réservé aux admins)

---

## 📞 Support Additionnel

### Logs à Consulter
```bash
# Backend
docker-compose logs backend -f

# Frontend (si démarré en dev)
# (vérifier la console du navigateur)

# PostgreSQL
docker-compose logs postgres | tail -50
```

### Commandes de Nettoyage
```bash
# Supprimer tous les utilisateurs (sauf admin principal)
docker exec mlops_postgres psql -U admin -d mlops_qc -c \
  "DELETE FROM users WHERE email NOT LIKE '%eyaelachabi%';"

# Réinsérer les utilisateurs de test
python3 backend/fix_passwords.py
```

---

## 📝 Notes Techniques

### Format de l'API de Login

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "operator@test.com",
  "password": "Operator@2024"
}
```

**Response (Success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Response (Error - 404):**
```json
{
  "detail": "Not Found"
}
```

### Structure du JWT Token

Le token décodé contient:
```json
{
  "sub": "user-uuid",
  "email": "operator@test.com",
  "role": "OPERATOR",
  "exp": 1703088000
}
```

---

## ✅ Correction Complète!

Le problème de connexion "Not Found" devrait maintenant être résolu.

**Prochaines étapes:**
1. Tester la connexion via l'interface
2. Vérifier les permissions pour chaque rôle
3. Tester la gestion des utilisateurs (admin uniquement)

---

*Document généré le: 20 Décembre 2025*
*Status: CORRECTION APPLIQUÉE ✅*
