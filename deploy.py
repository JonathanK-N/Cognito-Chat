#!/usr/bin/env python3
"""
Script de déploiement automatique pour Cognito Chat
Utilise Railway.app pour un déploiement simple
"""

import os
import subprocess
import json

def create_railway_config():
    """Crée la configuration Railway"""
    config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python app.py",
            "healthcheckPath": "/",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE"
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration Railway créée")

def create_requirements():
    """Met à jour requirements.txt"""
    requirements = [
        "flask>=2.3.0",
        "python-dotenv>=1.0.0",
        "twilio>=8.0.0",
        "openai>=1.12.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "PyPDF2>=3.0.0",
        "Pillow>=10.0.0",
        "gunicorn>=21.0.0"
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    print("✅ Requirements.txt mis à jour")

def create_procfile():
    """Crée le Procfile pour le déploiement"""
    with open('Procfile', 'w') as f:
        f.write('web: gunicorn app:app --host 0.0.0.0 --port $PORT')
    
    print("✅ Procfile créé")

def setup_environment():
    """Configure les variables d'environnement"""
    env_template = """# Configuration Cognito Chat
OPENAI_API_KEY=sk-your-openai-key-here
TWILIO_ACCOUNT_SID=your-twilio-sid-here
TWILIO_AUTH_TOKEN=your-twilio-token-here
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
SECRET_KEY=CognitoChat2024!SecureFlaskKey#WhatsAppBot$RandomString789
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Fichier .env créé - CONFIGUREZ VOS CLÉS API!")
    else:
        print("ℹ️  Fichier .env existe déjà")

def deploy_instructions():
    """Affiche les instructions de déploiement"""
    print("\nINSTRUCTIONS DE DEPLOIEMENT:")
    print("\n1. RAILWAY (Recommandé - Gratuit):")
    print("   • Allez sur railway.app")
    print("   • Connectez votre GitHub")
    print("   • Importez ce projet")
    print("   • Ajoutez vos variables d'environnement")
    print("   • Déploiement automatique!")
    
    print("\n2. HEROKU:")
    print("   • heroku create votre-app")
    print("   • git push heroku main")
    print("   • heroku config:set OPENAI_API_KEY=...")
    
    print("\n3. RENDER:")
    print("   • Connectez GitHub sur render.com")
    print("   • Sélectionnez ce repo")
    print("   • Ajoutez les variables d'environnement")
    
    print("\nCONFIGURATION TWILIO:")
    print("   • Webhook URL: https://votre-app.railway.app/whatsapp")
    print("   • Méthode: POST")

if __name__ == "__main__":
    print("Configuration de deploiement Cognito Chat\n")
    
    create_railway_config()
    create_requirements()
    create_procfile()
    setup_environment()
    deploy_instructions()
    
    print("\nConfiguration terminee!")
    print("N'oubliez pas de configurer vos cles API dans .env")