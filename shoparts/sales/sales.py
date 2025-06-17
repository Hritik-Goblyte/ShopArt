import sqlite3      # For SQLite database connection
import datetime     # For handling date and time



def today_sales(conn):
    today = datetime.datetime.now().date()
    c = conn.cursor()
    c.execute("""
        SELECT SUM(total) FROM bills
        WHERE DATE(timestamp) = ?
    """, (today,))
    total = c.fetchone()[0]
    total = total if total is not None else 0.0
    print(f"\n📊 Total Sales Today ({today}): ₹{total:.2f}")




def get_monthly_sales(conn, year, month):
    """Get total sales for a specific month"""
    c = conn.cursor()
    month_str = f"{year:04d}-{month:02d}"
    c.execute("SELECT SUM(total) FROM bills WHERE strftime('%Y-%m', timestamp) = ?", (month_str,))
    return c.fetchone()[0] or 0.0

def get_daily_sales(conn, date):
    """Get total sales for a specific date"""
    c = conn.cursor()
    c.execute("SELECT SUM(total) FROM bills WHERE DATE(timestamp) = ?", (date,))
    return c.fetchone()[0] or 0.0

def get_range_sales(conn, start_date, end_date):
    """Get total sales for a date range"""
    c = conn.cursor()
    c.execute("SELECT SUM(total) FROM bills WHERE DATE(timestamp) BETWEEN ? AND ?", 
              (start_date, end_date))
    return c.fetchone()[0] or 0.0

def get_yearly_sales(conn, year):
    """Get total sales for a specific year"""
    c = conn.cursor()
    c.execute("SELECT SUM(total) FROM bills WHERE strftime('%Y', timestamp) = ?", (str(year),))
    return c.fetchone()[0] or 0.0


