#!/usr/bin/env python3
"""
Script pour mettre à jour les mots de passe des utilisateurs de test
Mot de passe universel: Eyaelach0200@
"""
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

if __name__ == "__main__":
    password = "Eyaelach0200@"
    hashed = hash_password(password)
    print(f"Mot de passe: {password}")
    print(f"Hash bcrypt: {hashed}")
    print()
    print("SQL pour mettre à jour les utilisateurs:")
    print(f"""
UPDATE users SET password_hash = '{hashed}' WHERE email = 'operator@test.com';
UPDATE users SET password_hash = '{hashed}' WHERE email = 'chef@test.com';
UPDATE users SET password_hash = '{hashed}' WHERE email = 'viewer@test.com';
UPDATE users SET password_hash = '{hashed}' WHERE email = 'admin@test.com';
""")
