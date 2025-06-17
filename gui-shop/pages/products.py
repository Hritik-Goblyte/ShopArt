import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection

class ProductManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = get_connection()

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        # --- Title ---
        title = tk.Label(self, text="Manage Products", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        # --- Treeview (Product List) ---
        columns = ("id", "name", "price", "stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- Form Inputs ---
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Stock:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.stock_entry = tk.Entry(form_frame)
        self.stock_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Action Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Product", command=self.update_product).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(side="left", padx=5)

    def load_products(self):
        self.tree.delete(*self.tree.get_children())
        c = self.conn.cursor()
        c.execute("SELECT id, name, price, stock FROM products")
        for row in c.fetchall():
            self.tree.insert('', 'end', values=row)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        pid, name, price, stock = item["values"]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, price)
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, stock)

    def add_product(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        stock = self.stock_entry.get()
        if not name or not price or not stock:
            messagebox.showwarning("Missing", "All fields are required.")
            return
        try:
            price = float(price)
            stock = int(stock)
            c = self.conn.cursor()
            c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            self.conn.commit()
            self.load_products()
            self.clear_inputs()
            messagebox.showinfo("Success", "Product added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a product first.")
            return
        pid = self.tree.item(selected[0])["values"][0]
        name = self.name_entry.get()
        price = self.price_entry.get()
        try:
            price = float(price)
            stock = int(stock)
            c = self.conn.cursor()
            c.execute("UPDATE products SET name=?, price=? WHERE id=?", (name, price, pid))
            self.conn.commit()
            self.load_products()
            self.clear_inputs()
            messagebox.showinfo("Updated", "Product updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a product to delete.")
            return
        pid = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", "Delete this product?")
        if confirm:
            c = self.conn.cursor()
            c.execute("DELETE FROM products WHERE id=?", (pid,))
            self.conn.commit()
            self.load_products()
            self.clear_inputs()

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
