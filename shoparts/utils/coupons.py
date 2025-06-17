import random
import string
import datetime
from database.db import get_connection

def generate_coupon_code():
    prefix = random.choice(["SAVE", "OFFER", "DEAL", "GET"])
    discount = random.randint(15, 55)
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{discount}-{suffix}", discount

def generate_daily_coupons(conn,n=15):
    
    cursor = conn.cursor()

    # Clear previous day's coupons (optional: keep if you want history)
    today = datetime.date.today()
    cursor.execute("DELETE FROM discounts")
    conn.commit()

    codes = set()
    while len(codes) < n:
        code, discount = generate_coupon_code()
        if code not in codes:
            codes.add(code)
            cursor.execute(
                "INSERT INTO discounts (code, discount, used, created_at) VALUES (?, ?, ?, ?)",
                (code, discount, 0, datetime.datetime.now())
            )
    conn.commit()
    print(f"{n} new coupons generated.")
    conn.close()

# Run manually or via schedule
if __name__ == "__main__":
    generate_daily_coupons()
