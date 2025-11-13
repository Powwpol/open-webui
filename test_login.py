#!/usr/bin/env python3
"""Test de connexion Pulsai"""
import requests
import json

BASE_URL = "http://localhost:8080"
EMAIL = "paul.obara@pulsa-conseil.fr"
PASSWORD = "Pulsai120M"

print("🔐 Test de connexion Pulsai")
print("=" * 50)
print()

# 1. Vérifier le endpoint config
print("1️⃣ Vérification de la config...")
try:
    config = requests.get(f"{BASE_URL}/api/config")
    if config.status_code == 200:
        data = config.json()
        print(f"   ✅ Config accessible")
        print(f"   ENABLE_SIGNUP: {data.get('ENABLE_SIGNUP', 'N/A')}")
        print(f"   Version: {data.get('version', 'N/A')}")
    else:
        print(f"   ❌ Erreur config: {config.status_code}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
print()

# 2. Tester le signin
print("2️⃣ Test de connexion (signin)...")
try:
    signin_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auths/signin",
        json=signin_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ CONNEXION RÉUSSIE!")
        print(f"   Token: {result.get('token', 'N/A')[:50]}...")
        print(f"   User: {result.get('name', 'N/A')}")
        print()
        print("🎉 Votre compte fonctionne ! Essayez de vous connecter sur:")
        print(f"   http://localhost:8080/auth")
    else:
        print(f"   ❌ Échec: {response.text}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
print()

# 3. Vérifier les utilisateurs
print("3️⃣ Vérification des utilisateurs...")
try:
    import sqlite3
    conn = sqlite3.connect(r'.\pulsai-backend-data\webui.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, name, role FROM user')
    users = cursor.fetchall()
    print(f"   Utilisateurs: {len(users)}")
    for u in users:
        print(f"   - {u[1]} ({u[2]}) - {u[3]}")
    conn.close()
except Exception as e:
    print(f"   ❌ Erreur: {e}")






