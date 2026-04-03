"""
database.py — Couche d'accès aux données
  • PostgreSQL  quand DATABASE_URL est défini (Railway, prod)
  • SQLite      sinon (développement local)
"""
import os
import uuid
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

# ── Adaptateur de connexion ──────────────────────────────────────────────────

def _get_conn():
    """Retourne une connexion selon l'environnement."""
    if DATABASE_URL:
        import psycopg2
        # Railway fournit parfois postgres:// ; psycopg2 veut postgresql://
        url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        return psycopg2.connect(url)
    else:
        import sqlite3
        return sqlite3.connect('conversations.db')

def _ph():
    """Placeholder de paramètre : %s (psycopg2) ou ? (sqlite3)."""
    return '%s' if DATABASE_URL else '?'

def _serial():
    """Type auto-incrément selon le moteur."""
    return 'SERIAL' if DATABASE_URL else 'INTEGER'

def _autoincrement():
    return '' if DATABASE_URL else 'AUTOINCREMENT'

def _on_conflict_ignore():
    return 'ON CONFLICT DO NOTHING' if DATABASE_URL else 'OR IGNORE'

def _now_minus_7():
    """Expression 'il y a 7 jours' selon le moteur."""
    if DATABASE_URL:
        return "NOW() - INTERVAL '7 days'"
    return "datetime('now', '-7 days')"

def _returning_id():
    return 'RETURNING id' if DATABASE_URL else ''

# ── Initialisation du schéma ─────────────────────────────────────────────────

def init_db():
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()

    if DATABASE_URL:
        # ── PostgreSQL ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id          SERIAL PRIMARY KEY,
                username    TEXT UNIQUE NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin    INTEGER DEFAULT 0,
                last_login  TIMESTAMP,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id          SERIAL PRIMARY KEY,
                user_id     INTEGER,
                session_id  TEXT NOT NULL,
                numero      TEXT NOT NULL,
                type        TEXT NOT NULL,
                question    TEXT,
                reponse     TEXT,
                date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id          TEXT PRIMARY KEY,
                user_id     INTEGER,
                title       TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        # Admin par défaut
        import hashlib
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        ''', ('admin', 'admin@cognitochat.com', admin_hash, 1))

    else:
        # ── SQLite ──
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin      INTEGER DEFAULT 0,
                last_login    TIMESTAMP,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                session_id TEXT NOT NULL,
                numero     TEXT NOT NULL,
                type       TEXT NOT NULL,
                question   TEXT,
                reponse    TEXT,
                date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id         TEXT PRIMARY KEY,
                user_id    INTEGER,
                title      TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        # Colonnes manquantes (migrations légères SQLite)
        cursor.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'is_admin' not in cols:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        if 'last_login' not in cols:
            cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')
        cursor.execute("PRAGMA table_info(conversations)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'user_id' not in cols:
            cursor.execute('ALTER TABLE conversations ADD COLUMN user_id INTEGER')
        cursor.execute("PRAGMA table_info(chat_sessions)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'user_id' not in cols:
            cursor.execute('ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER')
        # Admin par défaut
        import hashlib
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@cognitochat.com', admin_hash, 1))

    conn.commit()
    conn.close()

# ── Utilisateurs ─────────────────────────────────────────────────────────────

def create_user(username, email, password_hash):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    try:
        if DATABASE_URL:
            cursor.execute(
                f'INSERT INTO users (username, email, password_hash) VALUES ({ph},{ph},{ph}) RETURNING id',
                (username, email, password_hash)
            )
            user_id = cursor.fetchone()[0]
        else:
            import sqlite3
            cursor.execute(
                f'INSERT INTO users (username, email, password_hash) VALUES ({ph},{ph},{ph})',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT id, username, email, password_hash FROM users WHERE email = {ph}',
        (email,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT id, username, email FROM users WHERE id = {ph}',
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def update_last_login(user_id):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {ph}',
        (user_id,)
    )
    conn.commit()
    conn.close()

# ── Conversations ─────────────────────────────────────────────────────────────

def save_conversation(session_id, user_id, numero, type_msg, question, reponse):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'INSERT INTO conversations (session_id, user_id, numero, type, question, reponse) VALUES ({ph},{ph},{ph},{ph},{ph},{ph})',
        (session_id, user_id, numero, type_msg, question, reponse)
    )
    cursor.execute(
        f'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = {ph}',
        (session_id,)
    )
    conn.commit()
    conn.close()

def get_conversations(limit=50):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT numero, type, question, reponse, date FROM conversations ORDER BY date DESC LIMIT {ph}',
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_conversation_history(session_id, limit=10):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT question, reponse FROM conversations WHERE session_id = {ph} ORDER BY date DESC LIMIT {ph}',
        (session_id, limit)
    )
    history = cursor.fetchall()
    conn.close()
    messages = []
    for question, reponse in reversed(history):
        if question:
            messages.append({'role': 'user', 'content': question})
        if reponse:
            messages.append({'role': 'assistant', 'content': reponse})
    return messages

# ── Sessions de chat ──────────────────────────────────────────────────────────

def create_chat_session(user_id):
    session_id = str(uuid.uuid4())
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f"INSERT INTO chat_sessions (id, user_id, title) VALUES ({ph},{ph},{ph})",
        (session_id, user_id, 'Nouvelle conversation')
    )
    conn.commit()
    conn.close()
    return session_id

def get_chat_sessions(user_id, limit=20):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT id, title, updated_at FROM chat_sessions WHERE user_id = {ph} ORDER BY updated_at DESC LIMIT {ph}',
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_session_messages(session_id):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'SELECT question, reponse, date FROM conversations WHERE session_id = {ph} ORDER BY date ASC',
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_session_title(session_id, title):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'UPDATE chat_sessions SET title = {ph} WHERE id = {ph}',
        (title, session_id)
    )
    conn.commit()
    conn.close()

def delete_chat_session(user_id, session_id):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(f'DELETE FROM conversations WHERE session_id = {ph}', (session_id,))
    cursor.execute(f'DELETE FROM chat_sessions WHERE id = {ph} AND user_id = {ph}', (session_id, user_id))
    conn.commit()
    conn.close()

# ── Admin ─────────────────────────────────────────────────────────────────────

def get_admin_stats():
    conn = _get_conn()
    cursor = conn.cursor()
    minus7 = _now_minus_7()

    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
    total_users = cursor.fetchone()[0]

    cursor.execute(f'SELECT COUNT(*) FROM users WHERE is_admin = 0 AND last_login >= {minus7}')
    active_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM chat_sessions')
    total_sessions = cursor.fetchone()[0]

    cursor.execute(f'SELECT COUNT(*) FROM users WHERE is_admin = 0 AND created_at >= {minus7}')
    new_users_week = cursor.fetchone()[0]

    conn.close()
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_conversations': total_conversations,
        'total_sessions': total_sessions,
        'new_users_week': new_users_week,
    }

def get_all_users():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.password_hash, u.last_login, u.created_at,
               COUNT(DISTINCT s.id) AS sessions_count,
               COUNT(DISTINCT c.id) AS messages_count
        FROM users u
        LEFT JOIN chat_sessions s ON s.user_id = u.id
        LEFT JOIN conversations  c ON c.user_id = u.id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username, u.email, u.password_hash, u.last_login, u.created_at
        ORDER BY u.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(f'DELETE FROM conversations WHERE user_id = {ph}', (user_id,))
    cursor.execute(f'DELETE FROM chat_sessions  WHERE user_id = {ph}', (user_id,))
    cursor.execute(f'DELETE FROM users          WHERE id = {ph}',      (user_id,))
    conn.commit()
    conn.close()

def reset_user_password(user_id, new_password_hash):
    conn = _get_conn()
    cursor = conn.cursor()
    ph = _ph()
    cursor.execute(
        f'UPDATE users SET password_hash = {ph} WHERE id = {ph}',
        (new_password_hash, user_id)
    )
    conn.commit()
    conn.close()
