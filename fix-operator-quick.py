#!/usr/bin/env python3
"""
Script de correction rapide pour l'utilisateur operator
"""

import subprocess
import json

print("=" * 60)
print("CORRECTION UTILISATEUR OPERATOR")
print("=" * 60)
print()

# 1. Vérifier et créer l'utilisateur dans PostgreSQL
print("1. Création/Mise à jour de l'utilisateur operator...")
print()

sql_commands = """
-- Supprimer l'ancien utilisateur s'il existe
DELETE FROM users WHERE email = 'operator@test.com';

-- Créer l'utilisateur avec le hash correct
INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'operator',
    'operator@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeY5GyYqXJflbeIm',
    'OPERATOR'::userrole,
    true,
    true,
    NOW(),
    NOW()
);

-- Afficher l'utilisateur créé
SELECT username, email, role, is_active FROM users WHERE email='operator@test.com';
"""

try:
    # Exécuter les commandes SQL
    result = subprocess.run(
        ['docker', 'exec', 'mlops_postgres', 'psql', '-U', 'admin', '-d', 'mlops_qc', '-c', sql_commands],
        capture_output=True,
        text=True
    )
    
    print("Résultat SQL:")
    print(result.stdout)
    if result.stderr:
        print("Erreurs:", result.stderr)
    
    print()
    print("✓ Utilisateur operator créé/mis à jour")
    print()
    
except Exception as e:
    print(f"❌ Erreur lors de la création: {e}")
    print()

# 2. Test de connexion
print("2. Test de connexion...")
print()

try:
    # Tester l'API
    import urllib.request
    import urllib.parse
    
    url = "http://localhost:8000/api/auth/login"
    data = json.dumps({
        "email": "operator@test.com",
        "password": "Operator@2024"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        print("✓ Connexion réussie!")
        print(f"✓ Token reçu: {result['access_token'][:50]}...")
        print()
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Erreur HTTP {e.code}: {error_body}")
        print()
        
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    print()

print("=" * 60)
print("IDENTIFIANTS DE CONNEXION")
print("=" * 60)
print("Email:        operator@test.com")
print("Mot de passe: Operator@2024")
print()
print("Connectez-vous sur: http://localhost:3000/auth/login")
print("=" * 60)
