import hashlib
import sqlite3

# Hash the password
password = "11644298Hr"
hashed_password = hashlib.sha256(password.encode()).hexdigest()

# Connect to your SQLite database
from database.db import get_connection  # if available
# Otherwise use: conn = sqlite3.connect("your_database_name.db")
conn = get_connection()
cursor = conn.cursor()

# Insert or update the password in the settings table
cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("password", hashed_password))

# Commit and close
conn.commit()
conn.close()

print("✅ Hashed password inserted successfully.")