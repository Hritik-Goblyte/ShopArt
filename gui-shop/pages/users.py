import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection
from utils.common import verify_password  # ✅ use reusable function
import os


def show_users(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    def handle_unlock():
        if verify_password(password_entry.get()):
            load_user_table()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    def load_user_table():
        for widget in content_frame.winfo_children():
            widget.destroy()

        tk.Label(content_frame, text="👤 Users", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        columns = ("id", "name", "phone", "email", "created_at")
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)

        headings = {
            "id": "ID",
            "name": "Name",
            "phone": "Phone",
            "email": "Email",
            "created_at": "Registered At"
        }

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, anchor="center", width=150)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("Treeview", font=("Arial", 10))

        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, name, phone, email, created_at FROM users ORDER BY created_at DESC")
            rows = c.fetchall()
            conn.close()

            if not rows:
                messagebox.showinfo("Info", "No users found.")
            else:
                for row in rows:
                    tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # --- Center-screen Password UI ---
    auth_frame = tk.Frame(content_frame, bg="white")
    auth_frame.place(relx=0.5, rely=0.4, anchor="center")

    tk.Label(auth_frame, text="🔐 Enter Password", font=("Arial", 14), bg="white").pack(pady=10)
    password_entry = tk.Entry(auth_frame, show="*", font=("Arial", 12), width=25)
    password_entry.pack(pady=5)

    tk.Button(auth_frame, text="🔓 Unlock", command=handle_unlock, bg="#2980b9", fg="white").pack(pady=10)
