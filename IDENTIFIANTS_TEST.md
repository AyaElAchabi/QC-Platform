# 🔐 IDENTIFIANTS DE TEST - Plateforme MLOps QC

## 📋 Liste des Comptes de Test

Pour l'instant, **tous les utilisateurs de test utilisent le même mot de passe** pour simplifier les tests.

### 🔑 Mot de passe universel
```
Eyaelach0200@
```

---

## 👤 Comptes Disponibles

### 1. 👑 Administrateur (ADMIN)

**Identifiants:**
- **Email:** `admin@test.com`
- **Password:** `Eyaelach0200@`

**Permissions:**
- ✅ Gestion complète des utilisateurs
- ✅ Créer/modifier/supprimer des projets
- ✅ Upload/annoter/supprimer des images
- ✅ Entraîner des modèles
- ✅ Télécharger des modèles
- ✅ Faire de l'inférence
- ✅ Voir tous les rapports
- ✅ Modifier les paramètres système

**Menus visibles:**
Dashboard | Projets | Images | Modèles | Inférence | Rapports | **Utilisateurs** | Paramètres

---

### 2. 👨‍💼 Chef Opérateur (CHEF_OPERATOR)

**Identifiants:**
- **Email:** `chef@test.com`
- **Password:** `Eyaelach0200@`

**Permissions:**
- ✅ Créer/modifier des projets
- ✅ Upload/annoter des images
- ✅ Entraîner des modèles
- ✅ Télécharger des modèles
- ✅ Faire de l'inférence
- ✅ Voir les rapports d'équipe
- ❌ **PAS** de gestion des utilisateurs
- ❌ **PAS** de suppression de projets

**Menus visibles:**
Dashboard | Projets | Images | Modèles | Inférence | Rapports | Paramètres

---

### 3. 👷 Opérateur (OPERATOR)

**Identifiants:**
- **Email:** `operator@test.com`
- **Password:** `Eyaelach0200@`

**Permissions:**
- ✅ Voir les projets
- ✅ Upload des images
- ✅ Annoter des images
- ✅ Faire de l'inférence
- ❌ **PAS** de création de projets
- ❌ **PAS** d'entraînement de modèles
- ❌ **PAS** de téléchargement de modèles
- ❌ **PAS** de rapports complets

**Menus visibles:**
Dashboard (limité) | Projets (lecture seule) | Images | Inférence | Paramètres

---

### 4. 👁️ Visualiseur (VIEWER)

**Identifiants:**
- **Email:** `viewer@test.com`
- **Password:** `Eyaelach0200@`

**Permissions:**
- ✅ Voir les projets
- ✅ Voir les images
- ✅ Voir les résultats d'inférence
- ❌ **AUCUNE** modification possible
- ❌ **PAS** d'upload d'images
- ❌ **PAS** d'annotations
- ❌ **PAS** d'inférence active
- ❌ **PAS** de création de projets

**Menus visibles:**
Dashboard (lecture seule) | Projets (lecture seule) | Images (lecture seule) | Paramètres

---

## 🧪 Guide de Test

### Comment tester chaque rôle :

1. **Déconnectez-vous** de votre compte actuel
   - Cliquez sur "Déconnexion" en bas de la sidebar

2. **Allez sur la page de login**
   ```
   http://localhost:3000/auth/login
   ```

3. **Connectez-vous avec un compte de test**
   - Utilisez un des emails ci-dessus
   - Mot de passe: `Eyaelach0200@`

4. **Observez les différences**
   - Menu de navigation (certains menus disparaissent)
   - Boutons d'action disponibles
   - Messages d'erreur si vous essayez une action interdite

5. **Testez les actions**
   - Essayez de créer un projet
   - Essayez d'uploader une image
   - Essayez d'entraîner un modèle
   - Certaines actions seront bloquées selon le rôle

---

## 🔍 Test Rapide des Connexions

Vous pouvez tester rapidement si tous les comptes fonctionnent :

```bash
# Admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Eyaelach0200@"}'

# Chef Opérateur
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"chef@test.com","password":"Eyaelach0200@"}'

# Opérateur
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@test.com","password":"Eyaelach0200@"}'

# Visualiseur
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"viewer@test.com","password":"Eyaelach0200@"}'
```

Si vous recevez un `access_token`, la connexion fonctionne ! ✅

---

## 💡 Astuces

### Tester plusieurs rôles en même temps
- Ouvrez plusieurs fenêtres de **navigation privée** (Incognito/Private)
- Connectez-vous avec un rôle différent dans chaque fenêtre
- Comparez les interfaces côte à côte

### Vérifier le rôle actuel
- En bas de la sidebar, vous verrez votre email et rôle
- Ouvrez la console (F12) et tapez:
  ```javascript
  localStorage.getItem('mlops_user_role')
  ```

### Forcer un rafraîchissement
- Si le menu ne change pas après connexion, appuyez sur `F5` ou `Cmd+R`

---

## 📊 Tableau Récapitulatif

| Action | Admin | Chef Op. | Opérateur | Viewer |
|--------|-------|----------|-----------|--------|
| Voir menu "Utilisateurs" | ✅ | ❌ | ❌ | ❌ |
| Créer un projet | ✅ | ✅ | ❌ | ❌ |
| Modifier un projet | ✅ | ✅ | ❌ | ❌ |
| Supprimer un projet | ✅ | ❌ | ❌ | ❌ |
| Upload images | ✅ | ✅ | ✅ | ❌ |
| Annoter images | ✅ | ✅ | ✅ | ❌ |
| Voir images | ✅ | ✅ | ✅ | ✅ |
| Entraîner modèle | ✅ | ✅ | ❌ | ❌ |
| Télécharger modèle | ✅ | ✅ | ❌ | ❌ |
| Faire inférence | ✅ | ✅ | ✅ | ❌ |
| Voir rapports | ✅ | ✅ (équipe) | ❌ | ❌ |
| Gérer utilisateurs | ✅ | ❌ | ❌ | ❌ |
| Changer rôles | ✅ | ❌ | ❌ | ❌ |

---

## ✅ Vérification

Pour vérifier que tous les comptes sont bien créés, reconnectez-vous en tant qu'admin (`eyaelachabi@gmail.com`) et allez sur la page "Utilisateurs". Vous devriez voir **7 utilisateurs** dont les 4 comptes de test.

---

**Date de création:** 20 Décembre 2025  
**Statut:** ✅ Opérationnel
