import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection
from datetime import date, timedelta
import os
import platform
import subprocess

def show_bills(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    def refresh_table(filter_type=None):
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        c = conn.cursor()

        query = "SELECT id, customer_name, total, timestamp FROM bills"
        params = ()

        if filter_type == "today":
            query += " WHERE DATE(timestamp) = ?"
            params = (date.today().isoformat(),)
        elif filter_type == "this_month":
            query += " WHERE strftime('%Y-%m', timestamp) = ?"
            params = (date.today().strftime("%Y-%m"),)
        elif filter_type == "last_month":
            first_day_this_month = date.today().replace(day=1)
            last_month = first_day_this_month - timedelta(days=1)
            query += " WHERE strftime('%Y-%m', timestamp) = ?"
            params = (last_month.strftime("%Y-%m"),)
        elif filter_type == "custom_date":
            date_filter = date_entry.get()
            query += " WHERE DATE(timestamp) = ?"
            params = (date_filter,)

        query += " ORDER BY timestamp DESC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        total_sum = 0
        for row in rows:
            tree.insert("", tk.END, values=row)
            total_sum += row[2]

        total_label.config(text=f"Total Sales: ₹{total_sum:.2f}")

    def view_bill():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a bill to view.")
            return

        values = tree.item(selected, "values")
        bill_id = values[0]
        pdf_path = f"bills/bill_{bill_id}.pdf"

        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"No PDF found for Bill #{bill_id}")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Darwin":
                subprocess.call(("open", pdf_path))
            else:
                subprocess.call(("xdg-open", pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open bill PDF:\n{e}")

    # ───── UI Starts ─────
    tk.Label(content_frame, text="🧾 Bills Summary", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    # Search frame
    search_frame = tk.Frame(content_frame, bg="white")
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Search by Date (YYYY-MM-DD):", bg="white").pack(side=tk.LEFT, padx=5)
    date_entry = tk.Entry(search_frame)
    date_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="🔍 Search", command=lambda: refresh_table("custom_date"), bg="#2980b9", fg="white").pack(side=tk.LEFT, padx=5)

    # Filter buttons
    btn_frame = tk.Frame(content_frame, bg="white")
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="📅 Today", command=lambda: refresh_table("today"), bg="#1abc9c", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="🗓 This Month", command=lambda: refresh_table("this_month"), bg="#f39c12", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📆 Last Month", command=lambda: refresh_table("last_month"), bg="#8e44ad", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📊 All", command=lambda: refresh_table(None), bg="#34495e", fg="white").pack(side=tk.LEFT, padx=5)

    # Bills table
    columns = ("bill_no", "customer_name", "total", "created_at")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, anchor="center", width=150)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
    style.configure("Treeview", font=("Arial", 10))
    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Action frame
    action_frame = tk.Frame(content_frame, bg="white")
    action_frame.pack(pady=5)
    tk.Button(action_frame, text="👁 View Bill", command=view_bill, bg="#2c3e50", fg="white").pack()

    # Total sales label
    total_label = tk.Label(content_frame, text="Total Sales: ₹0.00", font=("Arial", 12, "bold"), bg="white", fg="green")
    total_label.pack(pady=10)

    refresh_table("today")  # default load
