import sqlite3
from tabulate import tabulate  # Optional: For better table formatting

def show_discounts():
    # Connect to your database file
    conn = sqlite3.connect("shop.db")  # Change the file name if needed
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM discounts")
        rows = cursor.fetchall()

        if not rows:
            print("⚠ No coupons found in the discounts table.")
        else:
            headers = [description[0] for description in cursor.description]
            print(tabulate(rows, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    show_discounts()
