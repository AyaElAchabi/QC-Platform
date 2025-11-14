# 🔐 Correction de l'Authentification - Résumé

## Problème Identifié

Lorsque vous accédiez à `http://localhost:3000`, vous étiez directement redirigé vers le dashboard **sans passer par la page de login**, même après expiration du token JWT.

### Cause Racine

**Conflit entre localStorage et cookies** :
- Le middleware Next.js vérifie le token dans les **cookies** (`request.cookies.get('mlops_access_token')`)
- Le client API utilise le token depuis **localStorage**
- Quand le token expirait, l'API client supprimait uniquement localStorage, **pas le cookie**
- Le middleware voyait toujours le cookie expiré et considérait l'utilisateur comme authentifié

## Solution Implémentée

### 1. Création d'une Bibliothèque Utilitaire (`/frontend/src/lib/auth.ts`)

Fonctions pour synchroniser localStorage et cookies :

```typescript
- setAuthToken(token: string)     // Stocke dans localStorage ET cookies
- getAuthToken(): string | null   // Récupère de localStorage (avec fallback cookies)
- clearAuthToken()                // Supprime de localStorage ET cookies
- isAuthenticated(): boolean      // Vérifie la présence du token
```

### 2. Mise à Jour du Client API (`/frontend/src/lib/api/client.ts`)

**Avant** :
```typescript
// Lecture depuis localStorage uniquement
const token = localStorage.getItem("mlops_access_token");

// Suppression de localStorage uniquement en cas d'erreur 401/403
localStorage.removeItem("mlops_access_token");
```

**Après** :
```typescript
// Utilisation de la fonction utilitaire
const token = getAuthToken();

// Suppression synchronisée en cas d'erreur 401/403
clearAuthToken(); // Supprime localStorage ET cookies
```

### 3. Mise à Jour du Hook useAuth (`/frontend/src/lib/hooks/useAuth.ts`)

**Avant** :
```typescript
// Stockage manuel
localStorage.setItem("mlops_access_token", token);

// Suppression manuelle
localStorage.removeItem("mlops_access_token");
```

**Après** :
```typescript
// Utilisation des fonctions utilitaires
setAuthToken(response.access_token);  // Login/Register
clearAuthToken();                     // Logout
```

### 4. Mise à Jour de la Page de Login (`/frontend/src/app/(site)/auth/login/page.tsx`)

**Avant** :
```typescript
localStorage.setItem("mlops_access_token", data.access_token);
document.cookie = `mlops_access_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
```

**Après** :
```typescript
import { setAuthToken } from "@/lib/auth";
setAuthToken(data.access_token);
```

### 5. Amélioration du Middleware (`/frontend/src/middleware.ts`)

**Ajouts** :
- Logs pour debug (`console.log('🔒 Middleware: ...')`)
- Gestion explicite de la page d'accueil (`/`)
- Meilleure logique de redirection

## Comportement Attendu Après Correction

### Scénario 1 : Utilisateur NON connecté
1. Accès à `http://localhost:3000` → **Redirigé vers `/auth/login`**
2. Accès à `http://localhost:3000/dashboard` → **Redirigé vers `/auth/login`**
3. Accès à `http://localhost:3000/auth/login` → **Affiche la page de login**

### Scénario 2 : Utilisateur connecté (token valide)
1. Accès à `http://localhost:3000` → **Affiche la page d'accueil**
2. Accès à `http://localhost:3000/dashboard` → **Affiche le dashboard**
3. Accès à `http://localhost:3000/auth/login` → **Redirigé vers `/dashboard`**

### Scénario 3 : Token expiré (401/403 de l'API)
1. Appel API → **Erreur 401/403**
2. Intercepteur API → **Supprime localStorage ET cookies**
3. Redirection automatique → **`/auth/login`**
4. Prochain accès → **Middleware ne trouve pas de token → Redirection vers `/auth/login`**

### Scénario 4 : Déconnexion manuelle
1. Clic sur "Déconnexion" dans la sidebar
2. `clearAuthToken()` → **Supprime localStorage ET cookies**
3. Redirection → **`/auth/login`**

## Points de Synchronisation

| Action | localStorage | Cookies | Middleware | API Client |
|--------|-------------|---------|------------|------------|
| Login | ✅ Défini | ✅ Défini | ✅ Trouve le cookie | ✅ Trouve le token |
| Logout | ❌ Supprimé | ❌ Supprimé | ❌ Ne trouve pas le cookie | ❌ Ne trouve pas le token |
| Token expiré (401) | ❌ Supprimé | ❌ Supprimé | ❌ Ne trouve pas le cookie | ❌ Ne trouve pas le token |

## Test de Validation

### Manuel
```bash
chmod +x /Users/mac/mlops-qc-platform/test-auth.sh
/Users/mac/mlops-qc-platform/test-auth.sh
```

### Dans le navigateur
1. **Ouvrir** `http://localhost:3000`
2. **Vérifier** : Redirection vers `/auth/login` si non connecté
3. **Se connecter** avec vos identifiants
4. **Vérifier** : Redirection vers `/dashboard`
5. **Ouvrir la console du navigateur** (F12) et vérifier les logs :
   - `🔑 Token d'authentification sauvegardé` (lors du login)
   - `🔵 API Request: ...` (lors des appels API)
   - `🔒 Middleware: ...` (lors des redirections)
6. **Cliquer sur "Déconnexion"** dans la sidebar
7. **Vérifier** : Redirection vers `/auth/login`
8. **Vérifier dans la console** : `🔓 Token d'authentification supprimé`
9. **Retourner sur** `http://localhost:3000`
10. **Vérifier** : Redirection vers `/auth/login`

### Vérifier les cookies et localStorage
Dans la console du navigateur (F12) :
```javascript
// Vérifier localStorage
console.log('localStorage:', localStorage.getItem('mlops_access_token'));

// Vérifier cookies
console.log('cookies:', document.cookie);
```

**Attendu après login** :
- localStorage : `"eyJ..."`
- cookies : `mlops_access_token=eyJ...`

**Attendu après logout** :
- localStorage : `null`
- cookies : `""` (vide)

## Fichiers Modifiés

1. ✅ `/frontend/src/lib/auth.ts` (NOUVEAU)
2. ✅ `/frontend/src/lib/api/client.ts`
3. ✅ `/frontend/src/lib/hooks/useAuth.ts`
4. ✅ `/frontend/src/app/(site)/auth/login/page.tsx`
5. ✅ `/frontend/src/middleware.ts`

## Prochaines Étapes (Optionnel)

### Amélioration 1 : Refresh Token
Implémenter un système de refresh token pour éviter les déconnexions fréquentes.

### Amélioration 2 : Durée de Validité Configurable
Ajouter une configuration pour la durée de validité du token (actuellement 24h).

### Amélioration 3 : Message de Session Expirée
Afficher un message utilisateur clair quand la session expire.

### Amélioration 4 : Remember Me
Ajouter une option "Se souvenir de moi" pour prolonger la durée du cookie.

## Notes Techniques

### Pourquoi Synchroniser localStorage et Cookies ?
- **localStorage** : Accessible côté client (React components, API client)
- **Cookies** : Accessible côté serveur (Middleware Next.js)
- **Middleware Next.js s'exécute côté serveur** → Ne peut pas lire localStorage
- **Solution** : Dupliquer le token dans les deux emplacements

### Sécurité
- Cookie avec `SameSite=Lax` pour protection CSRF
- Token JWT avec expiration côté backend
- Suppression automatique en cas d'erreur d'authentification
- Pas de stockage en cookie HttpOnly (car besoin d'accès JavaScript pour API client)

### Performance
- Lecture de localStorage plus rapide que parsing des cookies
- `getAuthToken()` utilise localStorage en premier, cookies en fallback
- Pas d'impact significatif sur les performances

## Support

En cas de problème :
1. Vérifier les logs dans la console du navigateur (F12)
2. Vérifier les logs du middleware dans le terminal Next.js
3. Vérifier les logs du backend dans le terminal FastAPI
4. Supprimer manuellement localStorage et cookies et réessayer :
   ```javascript
   localStorage.clear();
   document.cookie.split(";").forEach(c => {
     document.cookie = c.trim().split("=")[0] + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC";
   });
   location.reload();
   ```
