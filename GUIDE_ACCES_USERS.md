# 🎯 GUIDE D'ACCÈS - Gestion des Utilisateurs

## 📍 Où trouver la gestion des utilisateurs ?

### Option 1 : Via le menu latéral (Sidebar) 👈

**Pour les administrateurs uniquement:**

1. Connectez-vous avec le compte admin (`eyaelachabi@gmail.com`)
2. Dans le menu de gauche, vous verrez l'option **"Utilisateurs"** avec une icône 👥
3. Cliquez dessus pour accéder directement à `/settings/users`

```
┌─────────────────────┐
│  MLOps QC           │
├─────────────────────┤
│  🏠 Dashboard       │
│  📁 Projets         │
│  🖼️  Images          │
│  🧠 Modèles         │
│  ⚡ Inférence       │
│  📊 Rapports        │
│  👥 Utilisateurs   │ ← ICI (Admin uniquement)
│  ⚙️  Paramètres     │
└─────────────────────┘
```

### Option 2 : Via la page Paramètres ⚙️

1. Connectez-vous avec le compte admin
2. Allez dans **Paramètres** (`/settings`)
3. En haut de la page, vous verrez une carte bleue **"Gestion des utilisateurs"**
4. Cliquez sur le bouton **"Accéder"**

```
┌──────────────────────────────────────────┐
│  📋 Paramètres                           │
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐  │
│  │ 👥 Gestion des utilisateurs        │  │
│  │ Gérer les utilisateurs...   [Accéder >] │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │ 👤 Profil                          │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### Option 3 : URL directe 🔗

Tapez directement dans votre navigateur:
```
http://localhost:3000/settings/users
```

---

## 🎨 Ce que vous verrez

### Interface de gestion des utilisateurs

```
┌────────────────────────────────────────────────────┐
│  Gestion des utilisateurs                          │
│  Gérez les utilisateurs, leurs rôles et permissions│
├────────────────────────────────────────────────────┤
│  🔍 [Rechercher...]        [Filtrer par rôle ▼]   │
├────────────────────────────────────────────────────┤
│  Email              Rôle          Statut   Actions │
├────────────────────────────────────────────────────┤
│  eya@gmail.com     🔴 Admin      ✅ Actif  [•••]   │
│  chef@test.com     🔵 Chef Op.   ✅ Actif  [•••]   │
│  operator@test.com 🟢 Opérateur  ✅ Actif  [•••]   │
│  viewer@test.com   ⚪ Viewer     ✅ Actif  [•••]   │
└────────────────────────────────────────────────────┘
```

### Fonctionnalités disponibles

✅ **Voir tous les utilisateurs** - Liste complète avec détails
✅ **Filtrer par rôle** - ADMIN, CHEF_OPERATOR, OPERATOR, VIEWER
✅ **Rechercher** - Par email
✅ **Changer le rôle** - Promouvoir/rétrograder les utilisateurs
✅ **Activer/Désactiver** - Gérer l'accès des utilisateurs
✅ **Supprimer** - Retirer un utilisateur (avec confirmation)

---

## 🔐 Permissions requises

### Pour accéder à `/settings/users`

- ✅ **ADMIN** - Accès complet
- ❌ **CHEF_OPERATOR** - Accès refusé
- ❌ **OPERATOR** - Accès refusé
- ❌ **VIEWER** - Accès refusé

**Note:** Seuls les administrateurs peuvent voir et accéder à la gestion des utilisateurs.

---

## 🚀 Test rapide

### 1. Connexion Admin
```bash
# URL: http://localhost:3000/auth/login
Email: eyaelachabi@gmail.com
Password: Eyaelach0200@
```

### 2. Navigation
- Option A: Cliquez sur **"Utilisateurs"** dans le menu de gauche
- Option B: Allez dans **Paramètres** → **"Gestion des utilisateurs"**
- Option C: Allez directement sur http://localhost:3000/settings/users

### 3. Vérification
Vous devriez voir:
- ✅ Liste de 7 utilisateurs
- ✅ Filtres et recherche fonctionnels
- ✅ Boutons d'action pour chaque utilisateur
- ✅ Badge de rôle avec couleurs

---

## 📸 Captures d'écran (à venir)

1. **Menu latéral** - Option "Utilisateurs" visible pour admin
2. **Page Paramètres** - Carte "Gestion des utilisateurs" en haut
3. **Page Utilisateurs** - Interface complète de gestion

---

## 🔧 En cas de problème

### Je ne vois pas l'option "Utilisateurs" dans le menu

**Cause:** Vous n'êtes pas connecté en tant qu'administrateur

**Solution:** 
1. Déconnectez-vous
2. Reconnectez-vous avec: `eyaelachabi@gmail.com` / `Eyaelach0200@`
3. Le menu "Utilisateurs" apparaîtra automatiquement

### J'obtiens "404 Not Found"

**Cause:** Le frontend n'a peut-être pas rechargé les modifications

**Solution:**
```bash
# Vérifier que le frontend tourne
lsof -ti:3000

# Si nécessaire, redémarrer le frontend
cd frontend
npm run dev
```

### La page ne charge pas les utilisateurs

**Cause:** Problème de connexion au backend

**Solution:**
```bash
# Tester l'API directement
./test-users-complete.sh

# Vérifier le backend
docker ps | grep mlops_backend
```

---

## 📞 Support

- 📖 Documentation complète: `AUTH_README.md`
- 🚀 Guide rapide: `QUICK_START_AUTH.md`
- ✅ Tests: `./test-users-complete.sh`
- 📊 Rapport: `FINAL_SUCCESS_REPORT.md`

---

**✅ Votre système est opérationnel !**

Le lien "Utilisateurs" est maintenant visible dans le menu latéral pour tous les administrateurs.
