# Cognito Chat — Assistant IA

**Cognito Chat** est un assistant intelligent créé par **Jonathan Kakesa**, CEO de Cognito Inc.  
Première version lancée le **22 mars 2022** à Kinshasa, République Démocratique du Congo.

Disponible via une interface web moderne et WhatsApp, Cognito Chat exploite GPT-4o, DALL-E 3 et Whisper pour offrir une expérience conversationnelle complète : texte, images, documents, audio.

---

## Fonctionnalités

### Chat Intelligent
- Réponses via **GPT-4o** avec mémoire conversationnelle (6 derniers échanges)
- **Recherche web** en temps réel (DuckDuckGo) pour les questions d'actualité
- Réponse dans la langue de l'utilisateur (français, anglais, lingala, swahili…)

### Génération d'images
- **DALL-E 3** intégré — déclenché automatiquement sur les demandes d'image
- Détection intelligente : demandes directes, logos, bannières, avatars
- Suivi contextuel : "Vas-y", "Ok", "Lance" relancent la génération depuis l'historique

### Génération de documents
- **PDF** — mise en page professionnelle avec en-tête Cognito, sections colorées
- **Word (.docx)** — document stylisé avec titres et listes
- **PowerPoint (.pptx)** — présentation thème sombre, accent violet, une diapo par section
- Téléchargement direct depuis le chat (bouton rouge/bleu/orange selon le format)

### Traitement de fichiers entrants
- **PDF** : extraction et analyse du texte
- **Images** : analyse visuelle avec GPT-4o Vision
- **Audio** : transcription avec Whisper-1 puis analyse GPT

### Interface Web
- Design futuriste, thème sombre/clair, palette violet/cyan
- Sessions multiples avec renommage automatique et suppression
- Rendu Markdown complet, boutons de copie, chips de démarrage rapide
- Interface responsive avec sidebar mobile

### Système Utilisateurs
- Authentification sécurisée (hachage mot de passe)
- Conversations isolées par utilisateur
- Panel administrateur : stats, gestion utilisateurs, graphique d'activité

### Intégration WhatsApp
- Webhook Twilio — réception automatique texte, image, PDF, audio
- Bot disponible 24/7

---

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/JonathanK-N/Cognito-Chat.git
cd Cognito-Chat
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Variables d'environnement
Créez un fichier `.env` à la racine :
```env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
SECRET_KEY=une-cle-secrete-longue
DATABASE_URL=postgresql://user:password@host:5432/dbname  # Railway
```

> Sans `DATABASE_URL`, l'app utilise SQLite en local automatiquement.

### 4. Lancer en local
```bash
python app.py
```

---

## Déploiement sur Railway

1. Connectez le repo GitHub à [Railway](https://railway.app)
2. Ajoutez un service **PostgreSQL** et copiez `DATABASE_URL` dans les variables de l'app
3. Ajoutez toutes les autres variables d'environnement
4. Railway déploie automatiquement à chaque push sur `main`

---

## Configuration WhatsApp

1. Créez un compte sur [twilio.com](https://twilio.com)
2. Activez le **WhatsApp Sandbox** dans la console Twilio
3. Configurez le webhook : `https://votre-app.up.railway.app/whatsapp`
4. Rejoignez le sandbox en envoyant `join [sandbox-name]` au numéro Twilio

---

## Administration

**Accès** : `/admin` (réservé aux comptes avec rôle admin)

| Fonctionnalité | Description |
|---|---|
| Statistiques | Utilisateurs, messages, sessions, activité |
| Gestion utilisateurs | Liste, réinitialisation de mot de passe, suppression |
| Graphique d'activité | Messages des 7 derniers jours (Chart.js) |

Compte admin par défaut :
- Email : `admin@cognitochat.com`
- Mot de passe : `admin123` *(à changer en production)*

---

## Architecture

```
Cognito-Chat/
├── app.py                    # Point d'entrée Flask
├── database.py               # Abstraction PostgreSQL / SQLite
├── requirements.txt
├── routes/
│   ├── auth.py               # Authentification (login, register, logout)
│   ├── admin.py              # Panel administrateur
│   ├── whatsapp.py           # Webhook Twilio WhatsApp
│   └── web.py                # Interface web (chat, download, sessions)
├── services/
│   ├── gpt_service.py        # GPT-4o, DALL-E 3, détection images
│   ├── file_generator.py     # Génération PDF, Word, PowerPoint
│   ├── search_service.py     # Recherche web DuckDuckGo
│   ├── pdf_service.py        # Extraction texte PDF
│   ├── whisper_service.py    # Transcription audio
│   └── tts_service.py        # Synthèse vocale
├── templates/
│   ├── index.html            # Interface principale du chat
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── admin/
│       ├── dashboard.html
│       └── users.html
└── static/                   # Assets CSS / JS / images
```

---

## Stack technique

| Couche | Technologies |
|---|---|
| Backend | Python 3, Flask, Gunicorn |
| Base de données | PostgreSQL (Railway) / SQLite (local) |
| IA | OpenAI GPT-4o, DALL-E 3, Whisper-1 |
| Génération de documents | fpdf2, python-docx, python-pptx |
| WhatsApp | Twilio API |
| Frontend | HTML5, CSS3, JavaScript vanilla, marked.js, Chart.js |
| Déploiement | Railway |

---

## Utilisation rapide

### Interface Web
1. Créez un compte ou connectez-vous
2. Tapez votre message — ou uploadez une image, un PDF, un fichier audio
3. Demandez une image : *"Génère un logo pour Cognito Inc."*
4. Demandez un document : *"Crée-moi une présentation PowerPoint sur le marketing digital"*
5. Téléchargez le fichier généré via le bouton dans la bulle de réponse

### WhatsApp
1. Rejoignez le sandbox Twilio
2. Envoyez n'importe quel message, image, PDF ou note vocale
3. Cognito Chat répond automatiquement

---

## Licence

Ce projet est la propriété de **Cognito Inc.**  
Contact : [jonathan.kakesa@cognito-inc.ca](mailto:jonathan.kakesa@cognito-inc.ca)
