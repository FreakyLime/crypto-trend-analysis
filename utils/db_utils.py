import sqlite3
from config.settings import SQLITE3_DATABASE_FILE
import logging

logger = logging.getLogger()

def insert_into_history(symbol, analysis, img):
    try:
        conn = sqlite3.connect(SQLITE3_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (symbol, analysis, img)
            VALUES (?, ?, ?)
        ''', (symbol, analysis, img))
        conn.commit()
    except sqlite3.Error as e:
        logger.warning(f"SQLite error: {e}")
    finally:
        conn.close()
