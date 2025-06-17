import tkinter as tk
from tkinter import ttk
from database.db import get_connection
from datetime import datetime, date, timedelta

def show_sales(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    tk.Label(content_frame, text="📦 Product-wise Sales Summary", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    search_frame = tk.Frame(content_frame, bg="white")
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Search by Date (YYYY-MM-DD):", bg="white").pack(side=tk.LEFT, padx=5)
    date_entry = tk.Entry(search_frame)
    date_entry.pack(side=tk.LEFT, padx=5)

    def refresh_table(filter_type=None):
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        c = conn.cursor()

        base_query = """
            SELECT p.name, SUM(bi.quantity) AS total_quantity, SUM(bi.quantity * bi.price) AS total_revenue
            FROM bill_items bi
            JOIN products p ON bi.product_id = p.id
            JOIN bills b ON bi.bill_id = b.id
        """
        where_clause = ""
        params = ()

        if filter_type == "today":
            where_clause = "WHERE DATE(b.timestamp) = ?"
            params = (date.today().isoformat(),)
        elif filter_type == "this_month":
            today = date.today()
            where_clause = "WHERE strftime('%Y-%m', b.timestamp) = ?"
            params = (today.strftime("%Y-%m"),)
        elif filter_type == "last_month":
            first_day = date.today().replace(day=1)
            last_month = first_day - timedelta(days=1)
            where_clause = "WHERE strftime('%Y-%m', b.timestamp) = ?"
            params = (last_month.strftime("%Y-%m"),)
        elif filter_type == "custom_date":
            date_filter = date_entry.get()
            where_clause = "WHERE DATE(b.timestamp) = ?"
            params = (date_filter,)

        final_query = f"{base_query} {where_clause} GROUP BY p.name ORDER BY total_quantity DESC"
        c.execute(final_query, params)
        rows = c.fetchall()
        

        grand_total = 0
        for row in rows:
            tree.insert("", tk.END, values=row)
            grand_total += row[2]

        total_label.config(text=f"Total Revenue: ₹{grand_total:.2f}")

    def search_by_date():
        refresh_table("custom_date")

    def load_today():
        refresh_table("today")

    def load_this_month():
        refresh_table("this_month")

    def load_last_month():
        refresh_table("last_month")

    def load_all():
        refresh_table(None)

    # Filter Buttons
    btn_frame = tk.Frame(content_frame, bg="white")
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="📅 Today's Sales", command=load_today, bg="#1abc9c", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="🗓 This Month", command=load_this_month, bg="#f39c12", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📆 Last Month", command=load_last_month, bg="#8e44ad", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📊 All Sales", command=load_all, bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="🔍 Search", command=search_by_date, bg="#2980b9", fg="white").pack(side=tk.LEFT, padx=5)

    # Table
    columns = ("product_name", "quantity_sold", "revenue")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, anchor="center")

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Total Label
    total_label = tk.Label(content_frame, text="Total Revenue: ₹0.00", font=("Arial", 12, "bold"), bg="white", fg="green")
    total_label.pack(pady=5)

    load_today()  # default
