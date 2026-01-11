# ⚡ FIX IMMÉDIAT - Erreur Connexion Operator

## 🚨 Erreur Actuelle
```
Erreur de connexion: {}
Not Found
```

---

## ✅ CORRECTION EN 3 COMMANDES

### 1️⃣ Créer l'utilisateur dans PostgreSQL

**Copiez-collez exactement cette commande:**

```bash
docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOF'
DELETE FROM users WHERE email = 'operator@test.com';
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (gen_random_uuid(), 'operator', 'operator@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'OPERATOR'::userrole, true, true, NOW(), NOW());
SELECT username, email, role FROM users WHERE email='operator@test.com';
EOF
```

### 2️⃣ Redémarrer le backend

```bash
cd /Users/mac/mlops-qc-platform && docker-compose restart backend
```

### 3️⃣ Tester

```bash
curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"operator@test.com","password":"Operator@2024"}'
```

---

## 🎯 IDENTIFIANTS

- **Email:** `operator@test.com`
- **Password:** `Operator@2024`  
- **Rôle:** OPERATOR

---

## 🔄 Si l'erreur persiste

### Vérifier que PostgreSQL fonctionne:
```bash
docker ps | grep postgres
```

### Vérifier que le backend fonctionne:
```bash
curl http://localhost:8000/health
```

### Voir les logs du backend:
```bash
docker-compose logs backend --tail=50
```

---

## 📝 CRÉER TOUS LES UTILISATEURS DE TEST

Si vous voulez créer tous les utilisateurs en une fois:

```bash
docker exec mlops_postgres psql -U admin -d mlops_qc <<'EOF'
-- Supprimer les anciens
DELETE FROM users WHERE email IN ('admin@test.com', 'chef@test.com', 'operator@test.com', 'viewer@test.com');

-- Admin
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (gen_random_uuid(), 'admin', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'ADMIN'::userrole, true, true, NOW(), NOW());

-- Chef
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (gen_random_uuid(), 'chef', 'chef@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'CHEF_OPERATOR'::userrole, true, true, NOW(), NOW());

-- Operator
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (gen_random_uuid(), 'operator', 'operator@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'OPERATOR'::userrole, true, true, NOW(), NOW());

-- Viewer
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (gen_random_uuid(), 'viewer', 'viewer@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'VIEWER'::userrole, true, true, NOW(), NOW());

-- Afficher le résultat
SELECT username, email, role FROM users ORDER BY role;
EOF
```

**Tous utilisent le même pattern de mot de passe:**
- admin@test.com → Admin@2024
- chef@test.com → Chef@2024  
- operator@test.com → Operator@2024
- viewer@test.com → Viewer@2024

---

## 🎉 TESTEZ MAINTENANT

Allez sur **http://localhost:3000/auth/login** et connectez-vous avec:
- **Email:** operator@test.com
- **Password:** Operator@2024

✅ Vous devriez être redirigé vers le dashboard!

---

*Dernière mise à jour: 20 Décembre 2025*
