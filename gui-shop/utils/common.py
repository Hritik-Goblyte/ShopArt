import hashlib
from database.db import get_connection

def get_setting(key):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def verify_password(input_password):
    hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    stored_hash = get_setting("password")
    return hashed_input == stored_hash
