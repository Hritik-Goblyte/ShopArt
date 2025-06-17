import tkinter as tk
from tkinter import messagebox
from utils.common import get_setting, verify_password
from database.db import get_connection
import hashlib

def show_settings(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    tk.Label(content_frame, text="⚙ Settings", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    form_frame = tk.Frame(content_frame, bg="white")
    form_frame.pack(padx=10, pady=10, fill=tk.X)

    # --- Tax Rate ---
    tk.Label(form_frame, text="Tax Rate (%):", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tax_label = tk.Label(form_frame, text=get_setting("tax_rate") or "Not Set", bg="white", fg="blue")
    tax_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # --- UPI ID ---
    tk.Label(form_frame, text="UPI ID:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    upi_label = tk.Label(form_frame, text=get_setting("bank_upi") or "Not Set", bg="white", fg="blue")
    upi_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # --- Password Change (just a label) ---
    tk.Label(form_frame, text="Admin Password:", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    tk.Label(form_frame, text="******", bg="white").grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Result/feedback label
    result_label = tk.Label(content_frame, text="", fg="green", bg="white", font=("Arial", 10, "bold"))
    result_label.pack()

    # --- Function to update a setting ---
    def update_setting(setting_key, prompt_label):
        result_label.config(text="", fg="green")
        pwd = simple_password_prompt()
        if not verify_password(pwd):
            result_label.config(text="❌ Invalid password", fg="red")
            return

        # Inline input
        for widget in form_frame.grid_slaves(row=3):  # clear any previous row 3 widgets
            widget.destroy()

        tk.Label(form_frame, text=f"New {prompt_label}:", bg="white").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        entry = tk.Entry(form_frame)
        entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(form_frame, text="Save", bg="#27ae60", fg="white",
                  command=lambda: save_new_setting(setting_key, entry.get(), prompt_label)).grid(row=3, column=2, padx=5)

    def simple_password_prompt():
        return tk.simpledialog.askstring("Authorization", "Enter admin password:", show="*")

    def save_new_setting(key, value, label_name):
        if key == "tax_rate":
            try:
                val = float(value)
                if not (0 <= val <= 100):
                    raise ValueError()
            except:
                result_label.config(text="❌ Invalid tax rate", fg="red")
                return

        elif key == "bank_upi":
            if "@" not in value or len(value) < 5:
                result_label.config(text="❌ Invalid UPI ID", fg="red")
                return

        elif key == "password":
            if len(value) < 4:
                result_label.config(text="❌ Password too short", fg="red")
                return
            # ✅ Hash the password before saving
            value = hashlib.sha256(value.encode()).hexdigest()

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
        except Exception as e:
            result_label.config(text=f"❌ Error saving setting: {e}", fg="red")
            return

        result_label.config(text=f"✅ {label_name} updated!", fg="green")

        # Refresh labels
        tax_label.config(text=get_setting("tax_rate") or "Not Set")
        upi_label.config(text=get_setting("bank_upi") or "Not Set")

        for widget in form_frame.grid_slaves(row=3):
            widget.destroy()


    # --- Buttons ---
    btn_frame = tk.Frame(content_frame, bg="white")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="✏️ Change Tax Rate", bg="#2980b9", fg="white",
              command=lambda: update_setting("tax_rate", "Tax Rate")).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="💳 Change UPI ID", bg="#8e44ad", fg="white",
              command=lambda: update_setting("bank_upi", "UPI ID")).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="🔐 Change Password", bg="#c0392b", fg="white",
              command=lambda: update_setting("password", "Password")).pack(side=tk.LEFT, padx=5)
