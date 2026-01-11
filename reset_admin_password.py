#!/usr/bin/env python3
"""
Reset admin password
"""
import bcrypt

password = "Admin@2024"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

print(f"Password: {password}")
print(f"Hash: {hashed}")
