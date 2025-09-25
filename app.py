from flask import Flask, session, redirect, url_for
from routes.whatsapp import whatsapp_bp
from routes.web import web_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from database import init_db
import os
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'CognitoChat2024!SecureFlaskKey#WhatsAppBot$RandomString789')

# Initialiser la base de données à la première requête
@app.before_first_request
def initialize_database():
    try:
        init_db()
    except Exception as e:
        print(f"Erreur DB: {e}")

# Enregistrer les blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(whatsapp_bp)
app.register_blueprint(web_bp)

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('web.index'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)