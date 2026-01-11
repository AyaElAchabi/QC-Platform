# 🚨 PROBLÈME: Menu Utilisateurs Absent

## Symptôme
Le menu "Utilisateurs" 👥 n'apparaît PAS dans la sidebar, même connecté en admin.

## Cause Probable
Le rôle de l'utilisateur n'est pas chargé depuis le JWT après connexion.

---

## ✅ SOLUTION RAPIDE

### 1️⃣ Ouvrir le navigateur
```
http://localhost:3000
```

### 2️⃣ Ouvrir DevTools (F12)
- Onglet **Console**

### 3️⃣ Exécuter ce code dans la Console

```javascript
// Décoder le JWT et extraire le rôle
const token = localStorage.getItem('mlops_access_token');
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  console.log('✅ Rôle trouvé:', payload.role);
  
  // Sauvegarder le rôle
  localStorage.setItem('mlops_user_role', payload.role);
  localStorage.setItem('mlops_user_email', payload.email);
  localStorage.setItem('mlops_user_id', payload.sub);
  
  console.log('✅ Données sauvegardées!');
  
  // Rafraîchir
  location.reload();
} else {
  console.log('❌ Pas de token. Reconnectez-vous.');
}
```

### 4️⃣ Résultat Attendu
Après le reload, vous devriez voir le menu **"Utilisateurs"** apparaître !

---

## 🔄 SI ÇA NE MARCHE PAS

### Étape A: Nettoyer et reconnecter

1. **F12** → **Application** → **Local Storage** → **http://localhost:3000**
2. **Supprimer TOUTES les clés**
3. Rafraîchir (Cmd+R)
4. Se reconnecter avec:
   - Email: `eyaelachabi@gmail.com`
   - Password: `Eyaelach0200@`
5. Vérifier que vous avez maintenant:
   - `mlops_user_role` = "ADMIN"
   - `mlops_user_email` = "eyaelachabi@gmail.com"

### Étape B: Vérifier les logs

Dans la Console (F12), vous devriez voir:
```
👤 Sidebar - User: { email: "...", role: "ADMIN", ... }
🔐 Sidebar - Role: ADMIN
```

Si vous voyez `Role: undefined`, recommencez l'Étape A.

---

## 📸 CAPTURES À ENVOYER SI ÇA NE MARCHE PAS

1. Console (F12) après connexion
2. Local Storage (F12 → Application → Local Storage)
3. La sidebar (menu de gauche)

---

**Essayez le script JavaScript dans la Console et dites-moi ce qui s'affiche !**
