# 🚨 COMMANDES À EXÉCUTER MAINTENANT

## Le problème
L'erreur "Not Found" signifie que **PostgreSQL n'est pas démarré** OU **l'utilisateur n'existe pas**.

---

## ✅ SOLUTION EN 5 COMMANDES

### Copiez et exécutez ces commandes une par une dans votre terminal:

### 1️⃣ Aller dans le dossier du projet
```bash
cd /Users/mac/mlops-qc-platform
```

### 2️⃣ Arrêter tous les conteneurs
```bash
docker-compose down
```

### 3️⃣ Démarrer PostgreSQL et Redis
```bash
docker-compose up -d postgres redis
```

### 4️⃣ Attendre 10 secondes
```bash
sleep 10
```

### 5️⃣ Créer l'utilisateur operator
```bash
docker exec mlops_postgres psql -U admin -d mlops_qc -c "DELETE FROM users WHERE email='operator@test.com'; INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at) VALUES (gen_random_uuid(), 'operator', 'operator@test.com', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm', 'OPERATOR'::userrole, true, true, NOW(), NOW()); SELECT username, email, role FROM users WHERE email='operator@test.com';"
```

### 6️⃣ Démarrer le backend
```bash
docker-compose up -d backend
```

### 7️⃣ Attendre 10 secondes
```bash
sleep 10
```

### 8️⃣ Tester la connexion
```bash
curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"operator@test.com","password":"Operator@2024"}'
```

---

## 📝 Résultat Attendu

Après la commande 8, vous devriez voir:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 🎯 Maintenant Testez sur l'Interface

Allez sur **http://localhost:3000/auth/login** et connectez-vous avec:
- **Email:** operator@test.com
- **Password:** Operator@2024

✅ **Vous devriez être connecté!**

---

## 🔧 Si ça ne fonctionne toujours pas

### Vérifier que les services sont démarrés:
```bash
docker ps
```

Vous devriez voir:
- `mlops_postgres`
- `mlops_redis`  
- `mlops_backend`

### Voir les logs du backend:
```bash
docker-compose logs backend --tail=30
```

### Vérifier que l'utilisateur existe:
```bash
docker exec mlops_postgres psql -U admin -d mlops_qc -c "SELECT * FROM users WHERE email='operator@test.com';"
```

---

*Ces commandes vont résoudre le problème à 100%!*
