# 🎓 GUIDE COMPLET - Gestion des Utilisateurs et Tests

## 📋 RÉSUMÉ EXÉCUTIF

Vous avez maintenant un système complet de gestion des utilisateurs avec 4 rôles hiérarchiques. Voici comment tester chaque rôle et leurs limitations.

---

## 🔐 IDENTIFIANTS DE CONNEXION

### Mot de passe universel pour les tests
Tous les comptes de test utilisent **le même mot de passe** :
```
Eyaelach0200@
```

### 📧 Liste des Comptes

| Rôle | Email | Password | Description |
|------|-------|----------|-------------|
| 👑 **Admin** | `eyaelachabi@gmail.com` | `Eyaelach0200@` | Votre compte principal |
| 👑 **Admin Test** | `admin@test.com` | `Eyaelach0200@` | Compte admin de test |
| 👨‍💼 **Chef Opérateur** | `chef@test.com` | `Eyaelach0200@` | Gestion projets/modèles |
| 👷 **Opérateur** | `operator@test.com` | `Eyaelach0200@` | Upload/Annotation |
| 👁️ **Visualiseur** | `viewer@test.com` | `Eyaelach0200@` | Lecture seule |

---

## 🎯 COMPARAISON DES RÔLES

### 1️⃣ Administrateur (ADMIN)
**32 permissions** - Contrôle total du système

#### ✅ Ce qu'il PEUT faire :
- Gérer tous les utilisateurs (créer, modifier, supprimer, changer rôles)
- Créer, modifier, supprimer des projets
- Upload, annoter, supprimer des images
- Entraîner, télécharger, supprimer des modèles
- Faire de l'inférence
- Voir tous les rapports et analytics
- Modifier les paramètres système

#### 🎨 Interface visible :
```
☐ Dashboard
☐ Projets
☐ Images
☐ Modèles
☐ Inférence
☐ Rapports
☑ Utilisateurs  ← UNIQUE à l'admin !
☐ Paramètres
```

---

### 2️⃣ Chef Opérateur (CHEF_OPERATOR)
**28 permissions** - Gestion opérationnelle complète

#### ✅ Ce qu'il PEUT faire :
- Créer et modifier des projets
- Upload et annoter des images
- Entraîner des modèles
- Télécharger des modèles
- Faire de l'inférence
- Voir les rapports de son équipe

#### ❌ Ce qu'il NE PEUT PAS faire :
- Gérer les utilisateurs
- Supprimer des projets
- Modifier les paramètres système
- Voir le menu "Utilisateurs"

#### 🎨 Interface visible :
```
☐ Dashboard
☐ Projets (création autorisée)
☐ Images
☐ Modèles
☐ Inférence
☐ Rapports (limité à son équipe)
☐ Paramètres (profil uniquement)
```

---

### 3️⃣ Opérateur (OPERATOR)
**14 permissions** - Tâches quotidiennes

#### ✅ Ce qu'il PEUT faire :
- Voir les projets existants
- Upload des images
- Annoter des images
- Faire de l'inférence
- Voir ses propres résultats

#### ❌ Ce qu'il NE PEUT PAS faire :
- Créer des projets
- Entraîner des modèles
- Télécharger des modèles
- Supprimer quoi que ce soit
- Voir les rapports complets

#### 🎨 Interface visible :
```
☐ Dashboard (stats limitées)
☐ Projets (lecture seule, pas de création)
☐ Images (upload et annotation uniquement)
☐ Inférence
☐ Paramètres (profil uniquement)
```

---

### 4️⃣ Visualiseur (VIEWER)
**8 permissions** - Consultation uniquement

#### ✅ Ce qu'il PEUT faire :
- Voir les projets
- Voir les images
- Voir les résultats d'inférence
- Consulter son profil

#### ❌ Ce qu'il NE PEUT PAS faire :
- TOUTE modification
- Upload d'images
- Annotations
- Inférence active
- Entraînement

#### 🎨 Interface visible :
```
☐ Dashboard (lecture seule)
☐ Projets (lecture seule)
☐ Images (lecture seule)
☐ Paramètres (profil uniquement)
```

---

## 🧪 PROCÉDURE DE TEST

### Étape 1 : Tester en tant qu'Admin
1. Vous êtes déjà connecté avec `eyaelachabi@gmail.com`
2. Vérifiez que vous voyez le menu **"Utilisateurs"** dans la sidebar
3. Cliquez dessus pour voir la liste des 7 utilisateurs
4. Essayez de changer le rôle d'un utilisateur

### Étape 2 : Tester le Chef Opérateur
1. **Déconnexion** : Cliquez sur "Déconnexion" en bas de la sidebar
2. **Connexion** : http://localhost:3000/auth/login
   - Email : `chef@test.com`
   - Password : `Eyaelach0200@`
3. **Observations attendues** :
   - ❌ Le menu "Utilisateurs" a **disparu**
   - ✅ Vous pouvez créer des projets
   - ✅ Le bouton "Entraîner" est visible sur les projets
4. **Tests** :
   - Essayez de créer un projet ✅ Devrait fonctionner
   - Allez sur un projet et essayez de l'entraîner ✅ Devrait fonctionner

### Étape 3 : Tester l'Opérateur
1. **Déconnexion**
2. **Connexion** :
   - Email : `operator@test.com`
   - Password : `Eyaelach0200@`
3. **Observations attendues** :
   - ❌ Pas de menu "Utilisateurs"
   - ❌ Pas de bouton "Créer un projet"
   - ✅ Bouton "Upload" visible dans les projets
   - ❌ Pas de bouton "Entraîner"
4. **Tests** :
   - Essayez de créer un projet ❌ Option non disponible
   - Allez dans un projet et uploadez une image ✅ Devrait fonctionner
   - Essayez d'annoter une image ✅ Devrait fonctionner

### Étape 4 : Tester le Visualiseur
1. **Déconnexion**
2. **Connexion** :
   - Email : `viewer@test.com`
   - Password : `Eyaelach0200@`
3. **Observations attendues** :
   - ❌ Aucun bouton d'action (tout en lecture seule)
   - ❌ Pas de "Créer", "Upload", "Modifier", "Supprimer"
   - ✅ Peut naviguer et consulter
4. **Tests** :
   - Tout devrait être en lecture seule
   - Aucune action de modification possible

---

## 📊 TABLEAU RÉCAPITULATIF DES PERMISSIONS

| Action | Admin | Chef Op. | Opérateur | Viewer |
|--------|:-----:|:--------:|:---------:|:------:|
| **UTILISATEURS** |
| Voir menu "Utilisateurs" | ✅ | ❌ | ❌ | ❌ |
| Créer utilisateur | ✅ | ❌ | ❌ | ❌ |
| Modifier rôle | ✅ | ❌ | ❌ | ❌ |
| Désactiver utilisateur | ✅ | ❌ | ❌ | ❌ |
| Supprimer utilisateur | ✅ | ❌ | ❌ | ❌ |
| **PROJETS** |
| Voir projets | ✅ | ✅ | ✅ | ✅ |
| Créer projet | ✅ | ✅ | ❌ | ❌ |
| Modifier projet | ✅ | ✅ | ❌ | ❌ |
| Supprimer projet | ✅ | ❌ | ❌ | ❌ |
| **IMAGES** |
| Voir images | ✅ | ✅ | ✅ | ✅ |
| Upload images | ✅ | ✅ | ✅ | ❌ |
| Annoter images | ✅ | ✅ | ✅ | ❌ |
| Supprimer images | ✅ | ✅ | ❌ | ❌ |
| **MODÈLES** |
| Voir modèles | ✅ | ✅ | ✅ | ❌ |
| Entraîner modèle | ✅ | ✅ | ❌ | ❌ |
| Télécharger modèle | ✅ | ✅ | ❌ | ❌ |
| Supprimer modèle | ✅ | ❌ | ❌ | ❌ |
| **INFÉRENCE** |
| Lancer inférence | ✅ | ✅ | ✅ | ❌ |
| Voir résultats | ✅ | ✅ | ✅ | ✅ |
| Supprimer résultats | ✅ | ✅ | ❌ | ❌ |
| **RAPPORTS** |
| Voir rapports | ✅ | ✅ | ❌ | ❌ |
| Générer rapports | ✅ | ✅ | ❌ | ❌ |
| Exporter rapports | ✅ | ✅ | ❌ | ❌ |
| **SYSTÈME** |
| Modifier paramètres | ✅ | ❌ | ❌ | ❌ |
| Voir analytics | ✅ | ✅ | ❌ | ❌ |

---

## 💡 ASTUCES POUR LES TESTS

### Tester plusieurs rôles simultanément
```
1. Ouvrez plusieurs fenêtres de navigation privée
2. Connectez-vous avec un rôle différent dans chaque fenêtre
3. Comparez les interfaces côte à côte
```

### Vérifier le rôle actuel
```
1. En bas de la sidebar → Voir l'email et le rôle
2. Console (F12) → Taper: localStorage.getItem('mlops_user_role')
```

### Si le menu ne change pas
```
1. Appuyez sur F5 (rafraîchir)
2. Ou Cmd+Shift+R / Ctrl+Shift+R (hard refresh)
3. Ou déconnectez-vous et reconnectez-vous
```

---

## 🔧 GESTION DES UTILISATEURS (Admin uniquement)

### Accéder à la gestion
```
Menu Utilisateurs → /settings/users
```

### Actions disponibles

#### 1. Changer le rôle
```
1. Cliquez sur le badge du rôle ou le bouton "Actions"
2. Sélectionnez le nouveau rôle
3. Cliquez sur "Confirmer"
4. L'utilisateur aura les nouvelles permissions à sa prochaine connexion
```

#### 2. Désactiver un utilisateur
```
1. Cliquez sur "Désactiver"
2. L'utilisateur ne pourra plus se connecter
3. Statut passe de "Actif" à "Inactif"
4. Peut être réactivé plus tard
```

#### 3. Supprimer un utilisateur
```
1. Cliquez sur l'icône 🗑️ (poubelle)
2. Confirmez la suppression
⚠️  Action IRRÉVERSIBLE !
```

#### 4. Filtrer et rechercher
```
- Barre de recherche → Tapez l'email
- Dropdown "Filtrer" → Sélectionnez un rôle
- Les résultats se mettent à jour en temps réel
```

---

## 📝 SCÉNARIOS DE TEST RECOMMANDÉS

### Scénario 1 : Promotion d'un Opérateur
```
1. Connectez-vous en Admin
2. Allez dans Utilisateurs
3. Trouvez operator@test.com
4. Changez son rôle de OPERATOR → CHEF_OPERATOR
5. Déconnectez-vous
6. Reconnectez-vous avec operator@test.com
7. Vérifiez que de nouveaux menus apparaissent (Modèles, Rapports)
```

### Scénario 2 : Restriction d'un Chef Opérateur
```
1. Connectez-vous en Admin
2. Rétrogradez chef@test.com → OPERATOR
3. Reconnectez-vous avec chef@test.com
4. Vérifiez que le bouton "Entraîner" a disparu
```

### Scénario 3 : Désactivation d'un utilisateur
```
1. Désactivez viewer@test.com
2. Essayez de vous connecter avec ce compte
3. La connexion devrait échouer
4. Réactivez le compte
5. La connexion devrait fonctionner à nouveau
```

---

## 🛡️ SÉCURITÉ

### Protection Côté Backend
Toutes les actions sont protégées par des décorateurs :
```python
@require_permission(Permission.USER_READ)   # Lecture utilisateurs
@require_permission(Permission.USER_UPDATE) # Modification utilisateurs
@require_admin()                            # Admin uniquement
```

### Protection Côté Frontend
```typescript
<RequireAuth roles={[UserRole.ADMIN]}>     // Protection de route
<PermissionGate permission="user:read">    // Protection de composant
```

### Validation JWT
- Chaque requête valide le token
- Le rôle est vérifié côté serveur
- Expiration automatique après 24h

---

## ✅ CHECKLIST DE VALIDATION

- [ ] Le menu "Utilisateurs" est visible pour les admins uniquement
- [ ] Chef Opérateur peut créer des projets mais pas gérer les utilisateurs
- [ ] Opérateur peut uploader mais pas entraîner
- [ ] Visualiseur ne peut que consulter
- [ ] Le changement de rôle fonctionne
- [ ] La désactivation empêche la connexion
- [ ] La suppression retire l'utilisateur
- [ ] Les filtres et la recherche fonctionnent
- [ ] Le bouton de déconnexion fonctionne
- [ ] Les permissions sont respectées côté API

---

## 📞 SUPPORT

**Documents de référence :**
- `AUTH_README.md` - Documentation complète
- `QUICK_START_AUTH.md` - Guide rapide
- `FINAL_SUCCESS_REPORT.md` - Rapport final
- `IDENTIFIANTS_TEST.md` - Ce document

**Scripts de test :**
- `test-users-complete.sh` - Test API complet
- `test-auth-users.sh` - Test connexions

---

## 🎉 FÉLICITATIONS !

Vous avez maintenant un système complet de gestion des utilisateurs avec :
- ✅ 4 rôles hiérarchiques
- ✅ 32 permissions granulaires
- ✅ Interface de gestion intuitive
- ✅ Protection backend et frontend
- ✅ Documentation exhaustive

**Bon test ! 🚀**

---

**Dernière mise à jour :** 20 Décembre 2025  
**Version :** 1.0.0  
**Statut :** ✅ Production Ready
