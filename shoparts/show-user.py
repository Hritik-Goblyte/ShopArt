import os
import time
from database.db import get_connection

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_all_user():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, phone, email, created_at FROM users")
        users = c.fetchall()
        conn.close()

        print(f"{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25} {'Created At'}")
        print("-" * 90)

        if not users:
            print("No users found.")
        else:
            for user in users:
                id_, name, phone, email, created_at = user

                # Safely handle None values
                name = name or ""
                phone = phone or ""
                email = email or ""
                created_at = str(created_at) if created_at else ""

                print(f"{id_:<5} {name:<20} {phone:<15} {email:<25} {created_at}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    try:
        while True:
            clear_terminal()
            print("Auto-Refreshing User List (Every 15s)...\n")
            show_all_user()
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nExited.")
