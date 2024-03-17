from config import DATABASE_FOLDER
from src.etc.storage import Connection

def test_database_connection():
    conn = Connection(DATABASE_FOLDER)
    conn.connect()
    assert conn.connected


