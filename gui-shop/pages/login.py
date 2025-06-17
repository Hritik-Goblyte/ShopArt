import tkinter as tk
from tkinter import messagebox
from pages.dashboard import show_dashboard
from utils.common import verify_password

def login_page(root):
    # Clear any existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Login function using hashed password verification
    def login():
        password = password_entry.get()
        if verify_password(password):
            show_dashboard(root)
        else:
            messagebox.showerror("Login Failed", "Incorrect password.")

    # UI Layout
    frame = tk.Frame(root, bg="white")
    frame.pack(expand=True)

    tk.Label(frame, text="Login", font=("Arial", 20, "bold"), bg="white").pack(pady=20)
    tk.Label(frame, text="Enter Password:", bg="white").pack()

    password_entry = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
    password_entry.pack(pady=10)

    tk.Button(frame, text="Login", font=("Arial", 12), bg="green", fg="white", command=login).pack(pady=10)
