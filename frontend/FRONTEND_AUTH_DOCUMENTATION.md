# Système d'Authentification et Gestion des Rôles - Frontend

## 📋 Vue d'ensemble

Implémentation complète du système d'authentification avec gestion des rôles et permissions granulaires pour la plateforme MLOps QC (Next.js 16 + TypeScript).

## 🎯 Rôles et Hiérarchie

### Hiérarchie des Rôles
```
ADMIN (Niveau 3)
   ↓
CHEF_OPERATOR (Niveau 2)
   ↓
OPERATOR (Niveau 1)
   ↓
VIEWER (Niveau 0)
```

### Permissions par Rôle

#### 👑 ADMIN - Administrateur
**Accès complet** à toutes les fonctionnalités :
- Gestion des utilisateurs (CRUD + gestion des rôles)
- Toutes les permissions des rôles inférieurs
- Accès aux logs d'audit
- Configuration système

#### 🔵 CHEF_OPERATOR - Chef Opérateur
**Gestion opérationnelle complète** :
- Création et gestion des projets
- Déploiement de modèles
- Gestion des entraînements (création, annulation)
- Validation des annotations
- Export des rapports
- Lecture des utilisateurs (pas de modification)

#### 🟢 OPERATOR - Opérateur
**Travail opérationnel quotidien** :
- Upload et annotation d'images
- Lancement d'entraînements
- Exécution d'inférences
- Génération XAI
- Création de feedback
- Lecture des projets et modèles

#### ⚪ VIEWER - Visualiseur
**Consultation uniquement** :
- Lecture des projets
- Consultation des modèles
- Vue des résultats d'entraînement
- Lecture des inférences et rapports
- Pas de modification possible

## 🏗️ Architecture

### Structure des Fichiers

```
frontend/src/
├── types/
│   ├── roles.ts              # Définition des rôles et permissions
│   └── auth.ts               # Types pour l'authentification
├── lib/
│   ├── auth.ts               # Utilitaires d'authentification
│   ├── api/
│   │   ├── auth.ts          # API d'authentification
│   │   └── users.ts         # API de gestion des utilisateurs
│   └── hooks/
│       └── useAuth.tsx       # Hook principal d'authentification
├── components/
│   ├── auth/
│   │   ├── RoleBadge.tsx    # Badge d'affichage de rôle
│   │   ├── RequireAuth.tsx  # Protection de routes
│   │   ├── PermissionGate.tsx # Affichage conditionnel
│   │   └── index.ts         # Exports
│   └── ui/
│       └── table.tsx        # Composant Table
└── app/
    ├── (site)/auth/
    │   ├── login/page.tsx   # Page de connexion
    │   └── register/page.tsx # Page d'inscription
    └── (app)/settings/users/
        └── page.tsx         # Gestion des utilisateurs (Admin)
```

## 🔧 Utilisation

### 1. Hook d'Authentification

```typescript
import { useAuth } from "@/lib/hooks/useAuth";

function MyComponent() {
  const {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    hasRole,
    hasPermission,
    isAdmin,
    isChefOrAdmin,
  } = useAuth();

  // Vérifier un rôle spécifique
  if (hasRole(UserRole.ADMIN)) {
    // Code pour admin uniquement
  }

  // Vérifier une permission
  if (hasPermission(Permission.PROJECT_CREATE)) {
    // Code pour création de projet
  }

  return (
    <div>
      <p>Connecté en tant que : {user?.email}</p>
      <RoleBadge role={user?.role} />
    </div>
  );
}
```

### 2. Protection de Routes

#### Méthode 1 : Composant RequireAuth

```typescript
import { RequireAuth } from "@/components/auth";
import { UserRole, Permission } from "@/types/roles";

export default function AdminPage() {
  return (
    <RequireAuth roles={[UserRole.ADMIN]}>
      <div>
        <h1>Page Admin</h1>
        {/* Contenu réservé aux admins */}
      </div>
    </RequireAuth>
  );
}

// Avec permissions spécifiques
export default function ProjectCreatePage() {
  return (
    <RequireAuth
      permissions={[Permission.PROJECT_CREATE]}
      fallbackUrl="/unauthorized"
    >
      <div>
        <h1>Créer un Projet</h1>
      </div>
    </RequireAuth>
  );
}
```

#### Méthode 2 : HOC withAuth

```typescript
import { withAuth } from "@/components/auth";
import { UserRole } from "@/types/roles";

function ChefOperatorDashboard() {
  return <div>Dashboard Chef Opérateur</div>;
}

export default withAuth(ChefOperatorDashboard, {
  roles: [UserRole.CHEF_OPERATOR, UserRole.ADMIN],
});
```

### 3. Affichage Conditionnel (PermissionGate)

```typescript
import { PermissionGate } from "@/components/auth";
import { Permission } from "@/types/roles";

function ProjectActions() {
  return (
    <div>
      {/* Toujours visible */}
      <Button>Voir le projet</Button>

      {/* Visible uniquement si permission */}
      <PermissionGate permissions={[Permission.PROJECT_UPDATE]}>
        <Button>Modifier le projet</Button>
      </PermissionGate>

      <PermissionGate
        permissions={[Permission.PROJECT_DELETE]}
        fallback={<p>Vous n'avez pas les droits de suppression</p>}
      >
        <Button variant="destructive">Supprimer</Button>
      </PermissionGate>
    </div>
  );
}
```

### 4. Badge de Rôle

```typescript
import { RoleBadge } from "@/components/auth";
import { UserRole } from "@/types/roles";

function UserCard({ user }) {
  return (
    <div className="flex items-center gap-2">
      <span>{user.email}</span>
      <RoleBadge role={user.role} />
    </div>
  );
}
```

### 5. Gestion des Utilisateurs (Admin)

La page `/settings/users` permet aux administrateurs de :
- Voir la liste de tous les utilisateurs
- Filtrer par rôle et rechercher
- Changer les rôles des utilisateurs
- Activer/désactiver des comptes
- Supprimer des utilisateurs

```typescript
// Accessible uniquement par les admins
// URL: /settings/users
```

## 🔐 API Endpoints

### Authentification

```typescript
// POST /api/auth/login
await authApi.login({ email, password });

// POST /api/auth/register
await authApi.register({ email, password, role });

// GET /api/auth/me
await authApi.getProfile();

// POST /api/auth/logout
await authApi.logout();
```

### Gestion des Utilisateurs (Admin uniquement)

```typescript
// GET /api/users - Liste des utilisateurs
await userManagementApi.getUsers({
  skip: 0,
  limit: 50,
  role: UserRole.OPERATOR,
  is_active: true,
});

// GET /api/users/:id - Détails d'un utilisateur
await userManagementApi.getUserById(userId);

// PUT /api/users/:id - Modifier un utilisateur
await userManagementApi.updateUser(userId, {
  email: "new@email.com",
  full_name: "John Doe",
});

// PUT /api/users/:id/role - Changer le rôle
await userManagementApi.changeUserRole(userId, UserRole.CHEF_OPERATOR);

// POST /api/users/:id/activate - Activer un utilisateur
await userManagementApi.activateUser(userId);

// POST /api/users/:id/deactivate - Désactiver un utilisateur
await userManagementApi.deactivateUser(userId);

// DELETE /api/users/:id - Supprimer un utilisateur
await userManagementApi.deleteUser(userId);

// GET /api/users/roles - Liste des rôles disponibles
await userManagementApi.getRoles();

// GET /api/users/:id/can-promote - Vérifier une promotion
await userManagementApi.checkPromotion(userId, UserRole.ADMIN);
```

## 📊 Matrice de Permissions

### Projets
| Permission | ADMIN | CHEF | OPERATOR | VIEWER |
|------------|-------|------|----------|--------|
| CREATE     | ✅ | ✅ | ❌ | ❌ |
| READ       | ✅ | ✅ | ✅ | ✅ |
| UPDATE     | ✅ | ✅ | ❌ | ❌ |
| DELETE     | ✅ | ✅ | ❌ | ❌ |

### Modèles
| Permission | ADMIN | CHEF | OPERATOR | VIEWER |
|------------|-------|------|----------|--------|
| UPLOAD     | ✅ | ✅ | ❌ | ❌ |
| READ       | ✅ | ✅ | ✅ | ✅ |
| DEPLOY     | ✅ | ✅ | ❌ | ❌ |
| DELETE     | ✅ | ✅ | ❌ | ❌ |

### Entraînements
| Permission | ADMIN | CHEF | OPERATOR | VIEWER |
|------------|-------|------|----------|--------|
| START      | ✅ | ✅ | ✅ | ❌ |
| READ       | ✅ | ✅ | ✅ | ✅ |
| CANCEL     | ✅ | ✅ | ❌ | ❌ |
| DELETE     | ✅ | ✅ | ❌ | ❌ |

### Annotations
| Permission | ADMIN | CHEF | OPERATOR | VIEWER |
|------------|-------|------|----------|--------|
| CREATE     | ✅ | ✅ | ✅ | ❌ |
| READ       | ✅ | ✅ | ✅ | ✅ |
| UPDATE     | ✅ | ✅ | ✅ | ❌ |
| VALIDATE   | ✅ | ✅ | ❌ | ❌ |

### Utilisateurs
| Permission | ADMIN | CHEF | OPERATOR | VIEWER |
|------------|-------|------|----------|--------|
| READ       | ✅ | ✅ | ✅ | ❌ |
| CREATE     | ✅ | ❌ | ❌ | ❌ |
| UPDATE     | ✅ | ❌ | ❌ | ❌ |
| DELETE     | ✅ | ❌ | ❌ | ❌ |
| MANAGE_ROLES | ✅ | ❌ | ❌ | ❌ |

## 🎨 Interface Utilisateur

### Couleurs des Badges

```typescript
ADMIN         → Badge violet (purple)
CHEF_OPERATOR → Badge bleu (blue)
OPERATOR      → Badge vert (green)
VIEWER        → Badge gris (gray)
```

### Pages Protégées

```
/dashboard                  → Tous les utilisateurs authentifiés
/projects                   → Tous les utilisateurs authentifiés
/projects/[id]              → Tous les utilisateurs authentifiés
/projects/create            → CHEF_OPERATOR, ADMIN
/models                     → Tous les utilisateurs authentifiés
/models/deploy              → CHEF_OPERATOR, ADMIN
/training                   → OPERATOR, CHEF_OPERATOR, ADMIN
/inference                  → OPERATOR, CHEF_OPERATOR, ADMIN
/settings/users             → ADMIN uniquement
/reports                    → Tous les utilisateurs authentifiés
```

## 🧪 Tests

### Tester l'authentification

```bash
# Se connecter en tant qu'admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Récupérer le profil
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

### Tester les permissions

```typescript
// Dans la console du navigateur
const auth = useAuth.getState();

// Vérifier les permissions
console.log(auth.hasPermission(Permission.PROJECT_CREATE));
console.log(auth.hasRole(UserRole.ADMIN));
console.log(auth.isChefOrAdmin());
```

## 🔄 Migration depuis l'ancien système

Si vous aviez un ancien système avec un simple champ `role: string` :

1. La migration backend convertit automatiquement les rôles
2. Le frontend utilise maintenant l'enum `UserRole`
3. Les anciennes valeurs sont mappées automatiquement :
   - `"admin"` → `UserRole.ADMIN`
   - `"chef_operator"` → `UserRole.CHEF_OPERATOR`
   - `"operator"` → `UserRole.OPERATOR`
   - `"viewer"` → `UserRole.VIEWER`

## 📝 Bonnes Pratiques

### 1. Toujours vérifier les permissions côté backend ET frontend
```typescript
// Frontend - Pour l'UX
<PermissionGate permissions={[Permission.PROJECT_DELETE]}>
  <DeleteButton />
</PermissionGate>

// Backend - Pour la sécurité
@require_permission(Permission.PROJECT_DELETE)
async def delete_project(project_id: str):
    # ...
```

### 2. Utiliser RequireAuth pour les pages complètes
```typescript
// Protéger une page entière
export default function AdminPage() {
  return (
    <RequireAuth roles={[UserRole.ADMIN]}>
      {/* Contenu */}
    </RequireAuth>
  );
}
```

### 3. Utiliser PermissionGate pour l'affichage conditionnel
```typescript
// Masquer/afficher des éléments
<PermissionGate permissions={[Permission.USER_CREATE]}>
  <CreateUserButton />
</PermissionGate>
```

### 4. Gérer les états de chargement
```typescript
const { user, isLoading } = useAuth();

if (isLoading) {
  return <LoadingSpinner />;
}
```

## 🚀 Prochaines Étapes

1. ✅ Système de rôles et permissions implémenté
2. ✅ Protection des routes frontend
3. ✅ Interface de gestion des utilisateurs
4. ✅ Badges de rôles
5. ⏳ Audit trail pour les changements de rôles
6. ⏳ Notifications pour les promotions/rétrogradations
7. ⏳ Permissions par projet (ownership)
8. ⏳ 2FA pour les comptes admin
9. ⏳ Sessions multiples et gestion des tokens
10. ⏳ Rate limiting par rôle

## 🐛 Dépannage

### Problème : "Property 'role' does not exist on type 'User'"
**Solution :** Assurez-vous d'avoir importé les types depuis `@/types/auth` et non depuis l'ancien système.

### Problème : Badge de rôle ne s'affiche pas
**Solution :** Vérifiez que le composant `Badge` UI existe dans `/components/ui/badge.tsx`.

### Problème : Redirection infinie sur les pages protégées
**Solution :** Vérifiez que `checkAuth()` est appelé au montage de l'application (dans le layout racine).

### Problème : 403 Forbidden sur l'API
**Solution :** Vérifiez que le token est bien envoyé dans les headers et qu'il n'a pas expiré.

## 📞 Support

Pour toute question ou problème :
1. Consulter la documentation backend : `/backend/AUTH_SYSTEM_DOCUMENTATION.md`
2. Vérifier les logs du serveur backend
3. Utiliser les outils de développement du navigateur (Network, Console)

---

**Version:** 1.0.0  
**Dernière mise à jour:** 19 décembre 2025  
**Auteur:** MLOps QC Platform Team
