# 🔧 Correction des Erreurs - Guide Rapide

## Problème

Erreur TypeScript : `Cannot find module '@/components/ui/alert'`

## Cause

- Cache TypeScript/VS Code non actualisé
- Le fichier `alert.tsx` a été créé mais pas encore détecté par l'IDE

## Solution

### Étape 1 : Vérifier que le fichier existe

```bash
ls -la /Users/mac/mlops-qc-platform/frontend/src/components/ui/alert.tsx
```

**Résultat attendu** : Le fichier doit exister (confirmé ✅)

### Étape 2 : Redémarrer le serveur TypeScript dans VS Code

**Option A - Dans VS Code** :
1. Ouvrir la palette de commandes : `Cmd + Shift + P`
2. Taper : "TypeScript: Restart TS Server"
3. Appuyer sur Entrée

**Option B - Recharger la fenêtre** :
1. Ouvrir la palette de commandes : `Cmd + Shift + P`
2. Taper : "Developer: Reload Window"
3. Appuyer sur Entrée

### Étape 3 : Nettoyer le cache Next.js

```bash
cd /Users/mac/mlops-qc-platform/frontend
rm -rf .next
```

### Étape 4 : Redémarrer le serveur de développement

```bash
# Si Next.js est en cours, l'arrêter d'abord
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Démarrer Next.js
npm run dev
```

## Vérification

Le serveur devrait démarrer sans erreurs. Si vous voyez encore l'erreur dans VS Code :

1. **Fermer VS Code complètement**
2. **Rouvrir VS Code**
3. **Ouvrir le projet** : `/Users/mac/mlops-qc-platform/frontend`
4. **Attendre** que TypeScript finisse d'indexer (vérifier la barre d'état en bas)

## Fichiers Créés/Modifiés

### Créés
1. ✅ `/frontend/src/components/ui/alert.tsx` - Composant Alert pour notifications

### Modifiés
1. ✅ `/frontend/src/app/(app)/projects/[id]/training/page.tsx` - Ajout vérification jobs actifs
2. ✅ `/frontend/src/lib/auth.ts` - Utilitaires d'authentification
3. ✅ `/frontend/src/lib/api/client.ts` - Synchronisation token
4. ✅ `/frontend/src/lib/hooks/useAuth.ts` - Utilisation des utilitaires auth

## Commandes Utiles

### Vérifier les erreurs TypeScript
```bash
cd /Users/mac/mlops-qc-platform/frontend
npx tsc --noEmit
```

### Vérifier les imports
```bash
cd /Users/mac/mlops-qc-platform/frontend
grep -r "from.*@/components/ui/alert" src/
```

### Rebuild complet
```bash
cd /Users/mac/mlops-qc-platform/frontend
rm -rf .next node_modules/.cache
npm run dev
```

## État Actuel

- ✅ Fichier `alert.tsx` créé et vérifié
- ✅ Code TypeScript correct
- ⚠️  Cache TypeScript/VS Code à rafraîchir

## Prochaine Étape

**Redémarrer le serveur TypeScript dans VS Code** ou **recharger la fenêtre** pour résoudre l'erreur.

---

**Note** : Cette erreur est normale après la création d'un nouveau fichier. VS Code et TypeScript ont besoin de recharger leur cache pour détecter les nouveaux fichiers.
