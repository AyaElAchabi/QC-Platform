#!/usr/bin/env python3
"""
Script pour corriger les mots de passe des utilisateurs de test
"""

import sys
import os
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration du mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/mlops_qc")

# Utilisateurs de test avec leurs mots de passe
TEST_USERS = [
    {
        "username": "admin",
        "email": "admin@test.com",
        "password": "Admin@2024",
        "role": "ADMIN"
    },
    {
        "username": "operator",
        "email": "operator@test.com",
        "password": "Operator@2024",
        "role": "OPERATOR"
    },
    {
        "username": "chef",
        "email": "chef@test.com",
        "password": "Chef@2024",
        "role": "CHEF_OPERATOR"
    },
    {
        "username": "viewer",
        "email": "viewer@test.com",
        "password": "Viewer@2024",
        "role": "VIEWER"
    }
]

def main():
    print("=" * 70)
    print("Correction des Mots de Passe des Utilisateurs de Test")
    print("=" * 70)
    print()
    
    try:
        # Créer la connexion à la base de données
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✓ Connexion à la base de données établie")
        print()
        
        # Pour chaque utilisateur
        for user_data in TEST_USERS:
            email = user_data["email"]
            password = user_data["password"]
            username = user_data["username"]
            role = user_data["role"]
            
            # Générer le hash du mot de passe
            password_hash = pwd_context.hash(password)
            
            print(f"Traitement de {email}...")
            print(f"  Username: {username}")
            print(f"  Role: {role}")
            print(f"  Password: {password}")
            print(f"  Hash: {password_hash[:50]}...")
            
            # Vérifier si l'utilisateur existe
            check_query = text("SELECT id FROM users WHERE email = :email")
            result = session.execute(check_query, {"email": email}).fetchone()
            
            if result:
                # Mettre à jour l'utilisateur existant
                update_query = text("""
                    UPDATE users 
                    SET password_hash = :password_hash,
                        username = :username,
                        role = :role,
                        is_active = true,
                        email_verified = true,
                        updated_at = NOW()
                    WHERE email = :email
                """)
                session.execute(update_query, {
                    "email": email,
                    "username": username,
                    "password_hash": password_hash,
                    "role": role
                })
                print(f"  ✓ Utilisateur mis à jour")
            else:
                # Créer le nouvel utilisateur
                insert_query = text("""
                    INSERT INTO users (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at)
                    VALUES (gen_random_uuid(), :username, :email, :password_hash, :role::userrole, true, true, NOW(), NOW())
                """)
                session.execute(insert_query, {
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "role": role
                })
                print(f"  ✓ Nouvel utilisateur créé")
            
            print()
        
        # Commit les changements
        session.commit()
        print("=" * 70)
        print("✓ Tous les utilisateurs ont été mis à jour avec succès!")
        print("=" * 70)
        print()
        
        # Afficher les utilisateurs
        print("Utilisateurs dans la base de données:")
        print("-" * 70)
        query = text("SELECT username, email, role, is_active FROM users ORDER BY role")
        users = session.execute(query).fetchall()
        
        for user in users:
            print(f"  {user[0]:15} | {user[1]:25} | {user[2]:15} | {'✓' if user[3] else '✗'}")
        
        print("-" * 70)
        print()
        
        # Instructions de test
        print("=" * 70)
        print("IDENTIFIANTS DE TEST")
        print("=" * 70)
        for user_data in TEST_USERS:
            print(f"  {user_data['email']:25} / {user_data['password']}")
        print()
        
        print("=" * 70)
        print("TEST DE CONNEXION")
        print("=" * 70)
        print("curl -X POST http://localhost:8000/api/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"email\":\"operator@test.com\",\"password\":\"Operator@2024\"}'")
        print()
        
        session.close()
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
