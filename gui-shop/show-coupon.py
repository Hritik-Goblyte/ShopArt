import os
import time
from database.db import get_connection

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_all_coupons():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, code, discount, used, created_at FROM discounts")
    coupons = c.fetchall()
    conn.close()

    print(f"{'ID':<5} {'Code':<15} {'Discount %':<12} {'Used':<6} {'Created At'}")
    print("-" * 60)
    if not coupons:
        print("No coupons found.")
    else:
        for coupon in coupons:
            id_, code, discount, used, created_at = coupon
            used_str = "Yes" if used else "No"
            print(f"{id_:<5} {code:<15} {discount:<12} {used_str:<6} {created_at}")

if __name__ == "__main__":
    try:
        while True:
            clear_terminal()
            print("Auto-Refreshing Coupon List (Every 15s)...\n")
            show_all_coupons()
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nExited.")
