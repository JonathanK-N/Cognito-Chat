# 🤖 Cognito Chat - Assistant IA WhatsApp

Un chatbot intelligent intégré à WhatsApp avec interface web moderne, capable de traiter du texte, des PDF, des images et de l'audio en utilisant les APIs OpenAI et Twilio.

## ✨ Fonctionnalités

### 💬 Chat Intelligent
- **Messages texte** : Réponses intelligentes via GPT-4o
- **Recherche web** : Informations en temps réel avec DuckDuckGo
- **Contexte conversationnel** : Mémorisation des échanges précédents

### 📁 Traitement de Fichiers
- **PDF** : Extraction et analyse de texte automatique
- **Images** : Analyse visuelle avec GPT-4o Vision
- **Audio** : Transcription avec Whisper puis analyse GPT

### 🌐 Interface Web Moderne
- **Design ChatGPT** : Interface utilisateur moderne et responsive
- **Sessions multiples** : Conversations séparées et organisées
- **Mode sombre/clair** : Thème adaptatif
- **Rendu Markdown** : Code syntax highlighting et formatage

### 👥 Système Utilisateurs
- **Authentification sécurisée** : Comptes utilisateurs individuels
- **Espaces privés** : Conversations isolées par utilisateur
- **Panel administrateur** : Gestion complète des utilisateurs

### 📱 Intégration WhatsApp
- **Webhook Twilio** : Réception automatique des messages
- **Multi-format** : Support texte, images, PDF, audio
- **Réponses automatiques** : Bot intelligent 24/7

## 🚀 Installation Rapide

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/cognito-chat.git
cd cognito-chat
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration
Créez un fichier `.env` :
```env
OPENAI_API_KEY=sk-votre-cle-openai
TWILIO_ACCOUNT_SID=votre-twilio-sid
TWILIO_AUTH_TOKEN=votre-twilio-token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
SECRET_KEY=votre-cle-secrete
```

### 4. Lancer l'application
```bash
python app.py
```

## 🌐 Déploiement

### Railway (Recommandé)
1. Connectez votre repo GitHub à [Railway](https://railway.app)
2. Ajoutez vos variables d'environnement
3. Déploiement automatique !

### Heroku
```bash
heroku create votre-app
git push heroku main
heroku config:set OPENAI_API_KEY=sk-...
```

## 📱 Configuration WhatsApp

1. **Compte Twilio** : Créez un compte sur [twilio.com](https://twilio.com)
2. **WhatsApp Sandbox** : Activez dans la console Twilio
3. **Webhook** : Configurez l'URL `https://votre-app.com/whatsapp`
4. **Test** : Envoyez `join [sandbox-name]` au numéro Twilio

## 🛡️ Administration

### Compte Admin par défaut
- **Email** : `admin@cognitochat.com`
- **Mot de passe** : `admin123`

### Fonctionnalités Admin
- 📊 Statistiques en temps réel
- 👥 Gestion des utilisateurs
- 🔑 Réinitialisation des mots de passe
- 🗑️ Suppression d'utilisateurs
- 📈 Graphiques d'activité

## 🏗️ Architecture

```
Cognito_Chat/
├── app.py                 # Point d'entrée Flask
├── database.py           # Gestion SQLite
├── routes/
│   ├── auth.py          # Authentification
│   ├── admin.py         # Panel administrateur
│   ├── whatsapp.py      # Webhook WhatsApp
│   └── web.py           # Interface web
├── services/
│   ├── gpt_service.py   # Intégration OpenAI
│   ├── search_service.py # Recherche web
│   ├── pdf_service.py   # Extraction PDF
│   ├── whisper_service.py # Transcription audio
│   └── tts_service.py   # Synthèse vocale
├── templates/           # Templates HTML
└── static/             # Assets CSS/JS
```

## 🔧 Technologies

- **Backend** : Flask, SQLite
- **IA** : OpenAI GPT-4o, Whisper
- **WhatsApp** : Twilio API
- **Frontend** : HTML5, CSS3, JavaScript
- **Recherche** : DuckDuckGo, Google News
- **Déploiement** : Railway, Heroku, Render

## 📝 Utilisation

### Interface Web
1. Créez un compte ou connectez-vous
2. Cliquez sur "Nouvelle conversation"
3. Tapez votre message ou uploadez un fichier
4. Profitez des réponses intelligentes !

### WhatsApp
1. Rejoignez le sandbox Twilio
2. Envoyez un message texte, image, PDF ou audio
3. Recevez une réponse automatique intelligente

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des fonctionnalités
- 🔧 Soumettre des pull requests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- 📧 Email : support@cognitochat.com
- 🐛 Issues : [GitHub Issues](https://github.com/votre-username/cognito-chat/issues)

---

⭐ **N'oubliez pas de mettre une étoile si ce projet vous plaît !** ⭐