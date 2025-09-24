import sqlite3
import uuid

# Migration de la base de données
def migrate_database():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    
    # Vérifier si la colonne session_id existe
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'session_id' not in columns:
        print("Migration de la base de données...")
        
        # Ajouter la colonne session_id
        cursor.execute('ALTER TABLE conversations ADD COLUMN session_id TEXT')
        
        # Créer une session par défaut pour les anciennes conversations
        default_session = str(uuid.uuid4())
        cursor.execute('UPDATE conversations SET session_id = ? WHERE session_id IS NULL', (default_session,))
        
        # Créer la table des sessions si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer une session pour les anciennes conversations
        cursor.execute('''
            INSERT OR IGNORE INTO chat_sessions (id, title)
            VALUES (?, ?)
        ''', (default_session, "Conversations précédentes"))
        
        conn.commit()
        print("Migration terminée !")
    else:
        print("Base de données déjà à jour.")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()