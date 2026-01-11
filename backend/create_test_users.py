#!/usr/bin/env python3
"""
Script pour créer des utilisateurs de test avec des mots de passe connus
"""
import sys
sys.path.insert(0, '/app')

from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import uuid

# Configuration
DATABASE_URL = "postgresql://admin:admin@localhost:5432/mlops_qc"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utilisateurs de test
TEST_USERS = [
    {
        "email": "admin@test.com",
        "password": "Admin123!",
        "role": "ADMIN",
        "description": "Administrateur de test - Tous les droits"
    },
    {
        "email": "chef@test.com",
        "password": "Chef123!",
        "role": "CHEF_OPERATOR",
        "description": "Chef Opérateur - Gestion projets et modèles"
    },
    {
        "email": "operator@test.com",
        "password": "Operator123!",
        "role": "OPERATOR",
        "description": "Opérateur - Upload images et annotations"
    },
    {
        "email": "viewer@test.com",
        "password": "Viewer123!",
        "role": "VIEWER",
        "description": "Visualiseur - Lecture seule"
    }
]

def create_test_users():
    engine = create_engine(DATABASE_URL)
    
    print("🔧 Création/Mise à jour des utilisateurs de test...")
    print("=" * 60)
    
    with Session(engine) as session:
        for user_data in TEST_USERS:
            email = user_data["email"]
            password = user_data["password"]
            role = user_data["role"]
            description = user_data["description"]
            
            # Hasher le mot de passe
            hashed_password = pwd_context.hash(password)
            
            # Vérifier si l'utilisateur existe
            result = session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                # Mettre à jour
                session.execute(
                    text("""
                        UPDATE users 
                        SET hashed_password = :password, 
                            role = :role,
                            is_active = true,
                            email_verified = true
                        WHERE email = :email
                    """),
                    {
                        "email": email,
                        "password": hashed_password,
                        "role": role
                    }
                )
                print(f"✅ Mis à jour: {email}")
            else:
                # Créer
                user_id = str(uuid.uuid4())
                session.execute(
                    text("""
                        INSERT INTO users (id, email, hashed_password, role, is_active, email_verified, created_at)
                        VALUES (:id, :email, :password, :role, true, true, NOW())
                    """),
                    {
                        "id": user_id,
                        "email": email,
                        "password": hashed_password,
                        "role": role
                    }
                )
                print(f"✅ Créé: {email}")
            
            print(f"   📧 Email: {email}")
            print(f"   🔑 Password: {password}")
            print(f"   👤 Rôle: {role}")
            print(f"   📝 Description: {description}")
            print()
        
        session.commit()
    
    print("=" * 60)
    print("✅ Tous les utilisateurs de test sont prêts !")
    print()
    print("📋 RÉSUMÉ DES IDENTIFIANTS:")
    print()
    for user_data in TEST_USERS:
        print(f"🔹 {user_data['role']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print()

if __name__ == "__main__":
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
