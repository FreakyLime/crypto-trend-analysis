import pytest
import sqlite3
from utils.db_utils import insert_into_history

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE history (
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            analysis TEXT NOT NULL,
            img TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return db_path

def test_insert_into_history(temp_db, mocker):
    mocker.patch('utils.db_utils.SQLITE3_DATABASE_FILE', temp_db)
    symbol = "BTC"
    analysis = "Test analysis"
    img = "test_image.png"

    insert_into_history(symbol, analysis, img)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history WHERE symbol = ?", (symbol,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "Row should not be None"
    assert row[1] == symbol, "Symbol should match"
    assert row[2] == analysis, "Analysis should match"
    assert row[3] == img, "Image should match"