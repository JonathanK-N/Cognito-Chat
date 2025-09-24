import sqlite3
from datetime import datetime
import os

DB_PATH = 'conversations.db'

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vérifier et ajouter les colonnes admin si nécessaires
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
    
    if 'last_login' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')
    
    # Créer un admin par défaut si aucun n'existe
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        import hashlib
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@cognitochat.com', admin_password, 1))
    
    # Créer la table conversations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT NOT NULL,
            numero TEXT NOT NULL,
            type TEXT NOT NULL,
            question TEXT,
            reponse TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Créer la table des sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Vérifier et ajouter user_id si nécessaire
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE conversations ADD COLUMN user_id INTEGER')
    
    cursor.execute("PRAGMA table_info(chat_sessions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER')
    
    conn.commit()
    conn.close()

def create_user(username, email, password_hash):
    """Crée un nouvel utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Récupère un utilisateur par email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    return user

def get_user_by_id(user_id):
    """Récupère un utilisateur par ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return user

def save_conversation(session_id, user_id, numero, type_msg, question, reponse):
    """Sauvegarde une conversation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (session_id, user_id, numero, type, question, reponse)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, user_id, numero, type_msg, question, reponse))
    
    # Mettre à jour la session
    cursor.execute('''
        UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (session_id,))
    
    conn.commit()
    conn.close()

def get_conversations(limit=50):
    """Récupère l'historique des conversations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT numero, type, question, reponse, date
        FROM conversations
        ORDER BY date DESC
        LIMIT ?
    ''', (limit,))
    
    conversations = cursor.fetchall()
    conn.close()
    
    return conversations

def get_conversation_history(session_id, limit=10):
    """Récupère l'historique d'une session de chat"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT question, reponse
        FROM conversations
        WHERE session_id = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (session_id, limit))
    
    history = cursor.fetchall()
    conn.close()
    
    # Convertir en format messages pour GPT
    messages = []
    for question, reponse in reversed(history):  # Inverser pour ordre chronologique
        if question:
            messages.append({"role": "user", "content": question})
        if reponse:
            messages.append({"role": "assistant", "content": reponse})
    
    return messages

def create_chat_session(user_id):
    """Crée une nouvelle session de chat pour un utilisateur"""
    import uuid
    session_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_sessions (id, user_id, title)
        VALUES (?, ?, ?)
    ''', (session_id, user_id, "Nouvelle conversation"))
    
    conn.commit()
    conn.close()
    
    return session_id

def get_chat_sessions(user_id, limit=20):
    """Récupère la liste des sessions de chat d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, updated_at
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

def update_session_title(session_id, title):
    """Met à jour le titre d'une session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE chat_sessions SET title = ? WHERE id = ?
    ''', (title, session_id))
    
    conn.commit()
    conn.close()

def get_session_messages(session_id):
    """Récupère tous les messages d'une session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT question, reponse, date
        FROM conversations
        WHERE session_id = ?
        ORDER BY date ASC
    ''', (session_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return messages

def update_last_login(user_id):
    """Met à jour la dernière connexion d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def get_admin_stats():
    """Récupère les statistiques pour l'admin"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nombre total d'utilisateurs
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
    total_users = cursor.fetchone()[0]
    
    # Utilisateurs actifs (connectés dans les 7 derniers jours)
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE is_admin = 0 AND last_login >= datetime('now', '-7 days')
    ''')
    active_users = cursor.fetchone()[0]
    
    # Nombre total de conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cursor.fetchone()[0]
    
    # Nombre total de sessions
    cursor.execute('SELECT COUNT(*) FROM chat_sessions')
    total_sessions = cursor.fetchone()[0]
    
    # Nouveaux utilisateurs cette semaine
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE is_admin = 0 AND created_at >= datetime('now', '-7 days')
    ''')
    new_users_week = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_conversations': total_conversations,
        'total_sessions': total_sessions,
        'new_users_week': new_users_week
    }

def get_all_users():
    """Récupère tous les utilisateurs pour l'admin"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, password_hash, last_login, created_at,
               (SELECT COUNT(*) FROM chat_sessions WHERE user_id = users.id) as sessions_count,
               (SELECT COUNT(*) FROM conversations WHERE user_id = users.id) as messages_count
        FROM users 
        WHERE is_admin = 0
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return users

def delete_user(user_id):
    """Supprime un utilisateur et toutes ses données"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Supprimer les conversations
    cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
    
    # Supprimer les sessions
    cursor.execute('DELETE FROM chat_sessions WHERE user_id = ?', (user_id,))
    
    # Supprimer l'utilisateur
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def reset_user_password(user_id, new_password_hash):
    """Réinitialise le mot de passe d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
    
    conn.commit()
    conn.close()