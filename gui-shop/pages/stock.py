import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database.db import get_connection
from datetime import datetime

def show_stock(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Title
    tk.Label(content_frame, text="📦 Stock Management", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    # Treeview for product stock
    columns = ("ID", "Name", "Price", "Stock")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Buttons
    btn_frame = tk.Frame(content_frame, bg="white")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="🔄 Refresh", bg="#3498db", fg="white", command=lambda: load_stock()).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="➕ Refill Stock", bg="#27ae60", fg="white", command=lambda: refill_stock()).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📜 View Stock History", bg="#8e44ad", fg="white", command=lambda: view_history()).pack(side=tk.LEFT, padx=5)

    def load_stock():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, price, stock FROM products")
        products = c.fetchall()
        conn.close()

        for product in products:
            tree.insert("", tk.END, values=product)

    from utils.common import verify_password

    def refill_stock():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to refill stock.")
            return

        values = tree.item(selected, "values")
        product_id, name, price, stock = values

        # 🔐 Prompt password before allowing stock refill
        password = simpledialog.askstring("Authorization", "Enter admin password:", show="*")
        if not verify_password(password):
            messagebox.showerror("Access Denied", "Invalid password.")
            return

        try:
            qty = simpledialog.askinteger("Refill Stock", f"Enter quantity to add for '{name}':")
            if qty is None or qty <= 0:
                return
            reason = simpledialog.askstring("Refill Reason", "Enter reason (e.g., Purchase, Correction):")
            if not reason:
                return
        except Exception:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, product_id))
        c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)", (product_id, qty, reason))
        conn.commit()
        conn.close()

        messagebox.showinfo("Stock Refilled", f"Stock updated for '{name}' (+{qty})")
        load_stock()


    def view_history():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to view stock history.")
            return

        values = tree.item(selected, "values")
        product_id, name = values[0], values[1]

        history_window = tk.Toplevel()
        history_window.title(f"Stock History - {name}")
        history_window.geometry("500x400")
        history_window.config(bg="white")

        tk.Label(history_window, text=f"📜 Stock History for {name}", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        hist_tree = ttk.Treeview(history_window, columns=("Change", "Reason", "Timestamp"), show="headings")
        for col in ("Change", "Reason", "Timestamp"):
            hist_tree.heading(col, text=col)
            hist_tree.column(col, anchor="center", width=150)

        hist_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT change, reason, timestamp FROM stock_history WHERE product_id = ? ORDER BY timestamp DESC", (product_id,))
        history = c.fetchall()
        conn.close()

        for record in history:
            hist_tree.insert("", tk.END, values=record)

    load_stock()
