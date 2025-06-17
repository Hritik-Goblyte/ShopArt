import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection
from utils.common import verify_password

import random
import string


def show_coupons(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    def verify_coupon_access():
        if verify_password(password_entry.get()):
            load_coupon_page()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    def load_coupon_page():
        for widget in content_frame.winfo_children():
            widget.destroy()

        tk.Label(content_frame, text="🎟 Coupon Codes", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        btn_frame = tk.Frame(content_frame, bg="white")
        btn_frame.pack(pady=5)

        def generate_coupons():
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM discounts")
            for _ in range(10):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                discount = random.randint(15, 55)
                c.execute("INSERT INTO discounts (code, discount, used) VALUES (?, ?, 0)", (code, discount))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "10 new coupons generated.")
            refresh_table()

        tk.Button(btn_frame, text="➕ Generate 10 Coupons", bg="#27ae60", fg="white", command=generate_coupons).pack()

        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        columns = ("code", "discount", "used")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True)

        def refresh_table():
            for i in tree.get_children():
                tree.delete(i)
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT code, discount, used FROM discounts ORDER BY used ASC")
            rows = c.fetchall()
            conn.close()
            for row in rows:
                used_text = "✅ Used" if row[2] else "❌ Unused"
                tree.insert("", tk.END, values=(row[0], f"{row[1]}%", used_text))

        refresh_table()

    # --- Password Entry UI ---
    auth_frame = tk.Frame(content_frame, bg="white")
    auth_frame.place(relx=0.5, rely=0.4, anchor="center")

    tk.Label(auth_frame, text="🔐 Enter Password", font=("Arial", 14), bg="white").pack(pady=10)
    password_entry = tk.Entry(auth_frame, show="*", font=("Arial", 12), width=25)
    password_entry.pack(pady=5)

    tk.Button(auth_frame, text="🔓 Unlock", command=verify_coupon_access, bg="#2980b9", fg="white").pack(pady=10)
