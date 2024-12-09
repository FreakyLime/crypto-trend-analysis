import sqlite3
from config.settings import SQLITE3_DATABASE_FILE

def apply_migrations():
    conn = sqlite3.connect(SQLITE3_DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        symbol TEXT,
        analysis TEXT,
        img TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("Migrations applied successfully.")

if __name__ == "__main__":
    apply_migrations()