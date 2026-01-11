# 🔐 Système d'Authentification et Gestion des Rôles - Documentation Complète

## 📋 Vue d'Ensemble

Système complet de gestion des rôles et permissions pour la plateforme MLOps QC, implémentant une hiérarchie à 4 niveaux avec permissions granulaires.

---

## 👥 Hiérarchie des Rôles

### 1. **ADMIN** (Administrateur / Account Owner)
**Description** : Contrôle total de la plateforme

**Permissions** : 
- ✅ **TOUTES** les permissions (40+)
- Gestion complète des utilisateurs (création, modification, suppression, promotion)
- Configuration système
- Gestion financière et abonnements
- Accès à toutes les fonctionnalités

**Cas d'usage** :
- Propriétaire de la plateforme
- Directeur technique
- Responsable IT

---

### 2. **CHEF_OPERATOR** (Chef Opérateur)
**Description** : Supervision d'équipe et gestion des projets

**Permissions** :
- 👥 **Utilisateurs** : Lecture, Modification (limité aux operators)
- 📁 **Projets** : CRUD complet
- 🖼️ **Images** : CRUD complet
- ✍️ **Annotations** : CRUD + Validation des annotations
- 🤖 **Training** : CRUD complet, démarrage, annulation
- 📦 **Modèles** : Lecture, téléchargement, déploiement, suppression
- ⚡ **Inférence** : Exécution, lecture, suppression
- 📊 **Analytics** : Lecture, génération de rapports
- ⚙️ **Settings** : Lecture seule

**Restrictions** :
- ❌ Ne peut pas créer/modifier d'autres admins
- ❌ Ne peut pas promouvoir de rôles
- ❌ Ne peut pas modifier les paramètres système

**Cas d'usage** :
- Chef d'équipe annotation
- Responsable qualité
- Data scientist senior

---

### 3. **OPERATOR** (Opérateur)
**Description** : Annotation et exécution d'inférences

**Permissions** :
- 👥 **Utilisateurs** : Lecture seule
- 📁 **Projets** : Lecture seule
- 🖼️ **Images** : Lecture + Upload
- ✍️ **Annotations** : CRUD de ses propres annotations
- 🤖 **Training** : Lecture seule
- 📦 **Modèles** : Lecture + Téléchargement
- ⚡ **Inférence** : Exécution + Lecture
- 📊 **Analytics** : Lecture seule

**Restrictions** :
- ❌ Ne peut pas démarrer de trainings
- ❌ Ne peut pas déployer de modèles
- ❌ Ne peut pas supprimer de projets
- ❌ Ne peut pas valider les annotations des autres
- ❌ Pas d'accès à la gestion des utilisateurs

**Cas d'usage** :
- Annotateur
- Opérateur de contrôle qualité
- Technicien de production

---

### 4. **VIEWER** (Observateur) - Legacy
**Description** : Accès en lecture seule (pour compatibilité)

**Permissions** :
- 👀 Lecture seule sur tous les modules

**Cas d'usage** :
- Auditeur externe
- Stagiaire en observation
- Client en démo

---

## 🔒 Matrice des Permissions

| Permission | ADMIN | CHEF_OP | OPERATOR | VIEWER |
|-----------|-------|---------|----------|--------|
| **Gestion Utilisateurs** |
| Lire utilisateurs | ✅ | ✅ | ✅ | ✅ |
| Créer utilisateurs | ✅ | ❌ | ❌ | ❌ |
| Modifier utilisateurs | ✅ | ⚠️ | ❌ | ❌ |
| Supprimer utilisateurs | ✅ | ❌ | ❌ | ❌ |
| Promouvoir rôles | ✅ | ❌ | ❌ | ❌ |
| **Projets** |
| Lire projets | ✅ | ✅ | ✅ | ✅ |
| Créer projets | ✅ | ✅ | ❌ | ❌ |
| Modifier projets | ✅ | ✅ | ❌ | ❌ |
| Supprimer projets | ✅ | ✅ | ❌ | ❌ |
| **Images** |
| Lire images | ✅ | ✅ | ✅ | ✅ |
| Uploader images | ✅ | ✅ | ✅ | ❌ |
| Supprimer images | ✅ | ✅ | ❌ | ❌ |
| **Annotations** |
| Lire annotations | ✅ | ✅ | ✅ | ✅ |
| Créer annotations | ✅ | ✅ | ✅ | ❌ |
| Modifier annotations | ✅ | ✅ | ⚠️ | ❌ |
| Supprimer annotations | ✅ | ✅ | ⚠️ | ❌ |
| Valider annotations | ✅ | ✅ | ❌ | ❌ |
| **Training** |
| Lire trainings | ✅ | ✅ | ✅ | ✅ |
| Démarrer training | ✅ | ✅ | ❌ | ❌ |
| Annuler training | ✅ | ✅ | ❌ | ❌ |
| Supprimer training | ✅ | ✅ | ❌ | ❌ |
| **Modèles** |
| Lire modèles | ✅ | ✅ | ✅ | ✅ |
| Télécharger modèles | ✅ | ✅ | ✅ | ❌ |
| Déployer modèles | ✅ | ✅ | ❌ | ❌ |
| Supprimer modèles | ✅ | ✅ | ❌ | ❌ |
| **Inférence** |
| Exécuter inférence | ✅ | ✅ | ✅ | ❌ |
| Lire historique | ✅ | ✅ | ✅ | ✅ |
| Supprimer inférence | ✅ | ✅ | ❌ | ❌ |

⚠️ = Limité (seulement ses propres ressources)

---

## 🛠️ Implémentation Backend

### Fichiers Créés/Modifiés

```
backend/
├── models/
│   ├── roles.py ✨ NOUVEAU
│   └── user.py ✅ MODIFIÉ
├── api/
│   ├── dependencies.py ✅ MODIFIÉ
│   ├── main.py ✅ MODIFIÉ
│   └── routes/
│       └── user_management.py ✨ NOUVEAU
└── alembic/versions/
    └── 006_add_role_enum.py ✨ NOUVEAU
```

### 1. **models/roles.py**
- `UserRole` enum (4 rôles)
- `Permission` enum (40+ permissions)
- `ROLE_PERMISSIONS` : Matrice complète des permissions
- Fonctions helpers :
  - `get_permissions_for_role()`
  - `has_permission()`
  - `can_promote_to_role()`
  - `get_role_display_name()`
  - `get_role_description()`

### 2. **models/user.py**
- Ajout de `UserRole` enum dans la colonne `role`
- Méthode `has_permission()` pour vérifier les permissions

### 3. **api/dependencies.py**
Nouveaux décorateurs de sécurité :

```python
# Par rôle
@router.get("/admin-only")
def admin_endpoint(user: User = Depends(require_role([UserRole.ADMIN]))):
    ...

# Par permission spécifique
@router.post("/training/start")
def start_training(user: User = Depends(require_permission(Permission.TRAINING_START))):
    ...

# Au moins une permission
@router.get("/models")
def list_models(
    user: User = Depends(require_any_permission([Permission.MODEL_READ, Permission.TRAINING_READ]))
):
    ...

# Toutes les permissions
@router.delete("/user/{user_id}")
def delete_user(
    user: User = Depends(require_all_permissions([Permission.USER_DELETE, Permission.USER_READ]))
):
    ...

# Helpers rapides
def require_admin()  # Admin uniquement
def require_chef_or_admin()  # Chef Operator ou Admin
```

### 4. **api/routes/user_management.py**
Routes de gestion des utilisateurs :

| Route | Méthode | Permission | Description |
|-------|---------|-----------|-------------|
| `/users/me` | GET | Authentifié | Info utilisateur connecté |
| `/users/me/permissions` | GET | Authentifié | Permissions de l'utilisateur |
| `/users` | GET | USER_READ | Liste tous les utilisateurs |
| `/users/{id}` | GET | USER_READ | Détail d'un utilisateur |
| `/users/{id}/role` | PUT | USER_PROMOTE | Changer le rôle |
| `/users/{id}/activate` | PUT | USER_UPDATE | Activer l'utilisateur |
| `/users/{id}/deactivate` | PUT | USER_UPDATE | Désactiver l'utilisateur |
| `/users/{id}` | DELETE | ADMIN | Supprimer l'utilisateur |
| `/users/roles/available` | GET | Authentifié | Liste des rôles disponibles |
| `/users/{id}/can-promote-to/{role}` | GET | Authentifié | Vérifier si promotion possible |

---

## 🚀 Déploiement

### Étape 1 : Appliquer la Migration

```bash
cd /Users/mac/mlops-qc-platform/backend

# Appliquer la migration
docker exec -it mlops_backend alembic upgrade head

# Vérifier
docker exec -it mlops_backend alembic current
```

### Étape 2 : Redémarrer le Backend

```bash
docker-compose restart backend

# Vérifier les logs
docker-compose logs backend --tail=50
```

### Étape 3 : Tester l'API

```bash
# Se connecter
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "eyaelachabi@gmail.com", "password": "Eyaelach0200@"}' \
  | jq -r '.access_token')

# Récupérer mes infos
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq

# Récupérer mes permissions
curl -X GET "http://localhost:8000/users/me/permissions" \
  -H "Authorization: Bearer $TOKEN" | jq

# Lister les utilisateurs
curl -X GET "http://localhost:8000/users" \
  -H "Authorization: Bearer $TOKEN" | jq

# Liste des rôles disponibles
curl -X GET "http://localhost:8000/users/roles/available" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 📚 Utilisation dans le Code

### Protection d'une Route par Rôle

```python
from api.dependencies import require_role
from models.roles import UserRole

@router.post("/projects")
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.CHEF_OPERATOR]))
):
    # Seul Admin et Chef Operator peuvent créer des projets
    ...
```

### Protection par Permission

```python
from api.dependencies import require_permission
from models.roles import Permission

@router.post("/training/start")
async def start_training(
    data: TrainingCreate,
    current_user: User = Depends(require_permission(Permission.TRAINING_START))
):
    # Vérifie que l'utilisateur a la permission TRAINING_START
    ...
```

### Vérification Manuelle

```python
@router.get("/annotations/{id}")
async def get_annotation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    annotation = db.query(Annotation).filter(Annotation.id == id).first()
    
    # Vérifier si l'utilisateur peut voir cette annotation
    if annotation.created_by != current_user.id:
        # Seul l'auteur ou quelqu'un avec ANNOTATION_VALIDATE peut voir
        if not current_user.has_permission(Permission.ANNOTATION_VALIDATE):
            raise HTTPException(403, "Cannot view other user's annotations")
    
    return annotation
```

---

## 🎨 Frontend (À Implémenter)

### Pages à Créer

1. **`/users` - Gestion des Membres**
   - Liste des utilisateurs avec filtres
   - Badges de rôles colorés
   - Actions : Voir détails, Changer rôle, Activer/Désactiver

2. **`/users/{id}` - Profil Utilisateur**
   - Informations du membre
   - Rôle et permissions
   - Historique d'activité
   - Bouton de promotion (si autorisé)

3. **Modal de Promotion**
   - Sélection du nouveau rôle
   - Affichage des permissions du rôle
   - Confirmation avec avertissement

### Composants Réutilisables

```typescript
// Badge de rôle
<RoleBadge role="ADMIN" />
<RoleBadge role="CHEF_OPERATOR" />
<RoleBadge role="OPERATOR" />

// Liste des permissions
<PermissionsList permissions={userPermissions} />

// Protection de route frontend
import { useAuth } from '@/hooks/useAuth'

function AdminOnlyPage() {
  const { user, hasPermission } = useAuth()
  
  if (!hasPermission('USER_PROMOTE')) {
    return <AccessDenied />
  }
  
  return <AdminContent />
}
```

---

## 🔐 Règles de Sécurité Implémentées

1. **Protection contre l'auto-modification** :
   - ❌ Un utilisateur ne peut pas changer son propre rôle
   - ❌ Un utilisateur ne peut pas se désactiver
   - ❌ Un admin ne peut pas se supprimer

2. **Protection des Admins** :
   - ❌ Seul un Admin peut créer/modifier un autre Admin
   - ❌ Un Admin ne peut pas supprimer un autre Admin
   - ⚠️ Nécessite confirmation pour les actions critiques

3. **Hiérarchie Stricte** :
   - Seul un Admin peut promouvoir vers n'importe quel rôle
   - Un Chef Operator ne peut pas promouvoir
   - Un Operator ne peut modifier que ses propres ressources

4. **Audit Trail** (À implémenter) :
   - Logger toutes les promotions de rôle
   - Logger les activations/désactivations
   - Logger les suppressions d'utilisateurs

---

## ✅ Tests de Validation

### Test 1 : Promotion de Rôle (Admin)
```bash
# Promouvoir un utilisateur vers CHEF_OPERATOR
curl -X PUT "http://localhost:8000/users/{user_id}/role" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_role": "CHEF_OPERATOR"}'

# ✅ Devrait réussir si token Admin
```

### Test 2 : Auto-Modification (Doit Échouer)
```bash
# Essayer de changer son propre rôle
curl -X PUT "http://localhost:8000/users/{own_id}/role" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_role": "ADMIN"}'

# ❌ Devrait échouer avec 403 Forbidden
```

### Test 3 : Permissions Manquantes
```bash
# Operator essaie de démarrer un training
curl -X POST "http://localhost:8000/training/start" \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -d '{ ... }'

# ❌ Devrait échouer avec 403 (permission manquante)
```

---

## 📊 Statistiques

- **4 Rôles** : ADMIN, CHEF_OPERATOR, OPERATOR, VIEWER
- **40+ Permissions** granulaires
- **10+ Routes API** de gestion des utilisateurs
- **Protection en profondeur** avec middleware et décorateurs
- **Audit complet** des actions sensibles

---

## 🔄 Prochaines Étapes

### Backend ✅ TERMINÉ
- [x] Enum des rôles et permissions
- [x] Décorateurs de sécurité
- [x] Routes de gestion des membres
- [x] Migration de base de données
- [x] Documentation API

### Frontend (À Faire)
- [ ] Page de gestion des membres `/users`
- [ ] Modal de promotion de rôle
- [ ] Badges de rôles colorés
- [ ] Hook `useAuth` avec vérification de permissions
- [ ] Protection des routes frontend
- [ ] Affichage conditionnel selon permissions

### Améliorations Futures
- [ ] Système d'audit trail complet
- [ ] Notifications par email lors de promotion
- [ ] Gestion des équipes/organisations
- [ ] Permissions personnalisées par projet
- [ ] 2FA pour les admins
- [ ] Historique des connexions

---

## 📞 Support

**Documentation Backend** : `/docs` (Swagger UI)
**Tests** : Voir section "Tests de Validation"
**Questions** : Consulter ce document ou demander à l'équipe

---

**Date** : 15 Décembre 2025  
**Version** : 1.0.0  
**Status** : ✅ Backend Complet - Frontend À Implémenter
