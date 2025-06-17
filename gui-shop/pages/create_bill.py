import tkinter as tk
from tkinter import messagebox
from database.db import get_connection
from utils.pdf import generate_pdf
import datetime
import sqlite3

now = datetime.datetime.now()


def create_bill(content_frame):
    def clear_content():
        for widget in content_frame.winfo_children():
            widget.destroy()

    conn = get_connection()
    clear_content()
    items = []
    subtotal = 0.0
    tax_rate = 0  # default

    from utils.common import get_setting

    tax_value = get_setting("tax_rate")
    try:
        tax_rate = float(tax_value)
    except (ValueError, TypeError):
        tax_rate = 0.0


    def add_product():
        try:
            product_id = int(prod_id_entry.get())
            quantity = int(quantity_entry.get())
            c = conn.cursor()
            c.execute("SELECT id, name, price, stock FROM products WHERE id=?", (product_id,))
            product = c.fetchone()
            if not product:
                messagebox.showerror("Error", "Invalid Product ID!")
                return

            if product[3] < quantity:
                messagebox.showerror("Stock Error", f"Only {product[3]} left in stock!")
                return

            item_total = product[2] * quantity
            items.append({
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': quantity,
                'total': item_total
            })

            nonlocal subtotal
            subtotal += item_total
            update_bill_area()

        except ValueError:
            messagebox.showerror("Error", "Enter valid product ID and quantity!")

    def calculate_tax(subtotal, tax_rate):
        return subtotal * tax_rate / 100

    def update_bill_area():
        nonlocal subtotal
        bill_area.delete('1.0', tk.END)
        for item in items:
            bill_area.insert(tk.END, f"{item['quantity']} x {item['name']} @ ₹{item['price']} = ₹{item['total']}\n")
        tax_amount = calculate_tax(subtotal, tax_rate)
        total_estimate = subtotal + tax_amount
        total_label.config(text=f"₹ {total_estimate:.2f}")
        bill_area.insert(tk.END, f"\nSubtotal: ₹{subtotal:.2f}\nTax: ₹{tax_amount:.2f}\nTotal: ₹{total_estimate:.2f}\n")


    def clear_all():
        items.clear()
        bill_area.delete('1.0', tk.END)
        prod_id_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        total_label.config(text="₹ 0.00")
        name_entry.delete(0, tk.END)
        contact_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        coupon_entry.delete(0,tk.END)

    
    def generate_bill():
        if not items:
            messagebox.showerror("Empty", "No items added to bill!")
            return

        name = name_entry.get().strip()
        contact = contact_entry.get().strip()
        email = email_entry.get().strip()
        coupon = coupon_entry.get().strip()

        discount = 0
        if coupon:
            c = conn.cursor()
            c.execute("SELECT discount FROM discounts WHERE used=0 AND code=?", (coupon,))
            row = c.fetchone()
            if row:
                discount = row[0]
            else:
                messagebox.showinfo("Coupon", "Invalid or already used coupon.")
                return

        tax_amount = calculate_tax(subtotal, tax_rate)
        total = subtotal + tax_amount
        if discount > 0:
            total -= subtotal * discount / 100

        payment = payment_var.get()
        if payment not in ['Cash', 'Online']:
            messagebox.showerror("Payment", "Select payment mode!")
            return

        timestamp = datetime.datetime.now().isoformat()
        now = datetime.datetime.now()

        c = conn.cursor()
        c.execute("INSERT INTO bills (customer_name, total, payment_mode, timestamp, pdf_path) VALUES (?, ?, ?, ?, '')",
                (name, total, payment, timestamp))
        bill_id = c.lastrowid

        pdf_path = generate_pdf(bill_id, name, contact, email, items, subtotal, tax_amount, total, tax_rate, payment, discount)
        c.execute("UPDATE bills SET pdf_path=? WHERE id=?", (pdf_path, bill_id))

        for item in items:
            c.execute("INSERT INTO bill_items (bill_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (bill_id, item['id'], item['quantity'], item['price']))
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['quantity'], item['id']))
            c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)",
                    (item['id'], -item['quantity'], f"Bill #{bill_id}"))

        if coupon:
            c.execute("UPDATE discounts SET used=1 WHERE code=?", (coupon,))

        # Insert user only if not already in DB
        if contact or email:
            c.execute("SELECT id FROM users WHERE phone = ? OR email = ?", (contact, email))
            existing_user = c.fetchone()
            if not existing_user:
                c.execute(
                    "INSERT INTO users (name, phone, email, created_at) VALUES (?, ?, ?, ?)",
                    (name, contact or None, email or None, now)
                )

        conn.commit()
        messagebox.showinfo("Bill Generated", f"Bill saved as PDF\n{pdf_path}")
        clear_all()



    # GUI Layout
    tk.Label(content_frame, text="Create Bill", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    cust_frame = tk.LabelFrame(content_frame, text="Customer Details", bg="white")
    cust_frame.pack(padx=10, pady=10, fill=tk.X)
    name_entry = tk.Entry(cust_frame)
    contact_entry = tk.Entry(cust_frame)
    email_entry = tk.Entry(cust_frame)
    for i, label in enumerate(["Customer Name:", "Contact:", "Email:"]):
        tk.Label(cust_frame, text=label, bg="white").grid(row=i, column=0, padx=5, pady=5, sticky='w')
    name_entry.grid(row=0, column=1, padx=5)
    contact_entry.grid(row=1, column=1, padx=5)
    email_entry.grid(row=2, column=1, padx=5)

    prod_frame = tk.LabelFrame(content_frame, text="Product Entry", bg="white")
    prod_frame.pack(padx=10, pady=10, fill=tk.X)
    prod_id_entry = tk.Entry(prod_frame)
    quantity_entry = tk.Entry(prod_frame)
    tk.Label(prod_frame, text="Product ID:", bg="white").grid(row=0, column=0, padx=5)
    tk.Label(prod_frame, text="Quantity:", bg="white").grid(row=0, column=2, padx=5)
    prod_id_entry.grid(row=0, column=1, padx=5)
    quantity_entry.grid(row=0, column=3, padx=5)
    tk.Button(prod_frame, text="Add to Bill", bg="green", fg="white", command=add_product).grid(row=0, column=4, padx=10)

    bill_area = tk.Text(content_frame, height=12, width=90, bd=1, relief=tk.SOLID)
    bill_area.pack(padx=10, pady=10)

    tk.Label(content_frame, text="Coupon Code:", bg="white").pack()
    coupon_entry = tk.Entry(content_frame)
    coupon_entry.pack(pady=5)

    bottom_frame = tk.Frame(content_frame, bg="white")
    bottom_frame.pack(fill=tk.X, padx=10, pady=5)

    payment_var = tk.StringVar()
    tk.Label(bottom_frame, text="Payment:", bg="white").pack(side=tk.LEFT, padx=5)
    tk.OptionMenu(bottom_frame, payment_var, "Cash", "Online").pack(side=tk.LEFT)

    total_label = tk.Label(bottom_frame, text="₹ 0.00", font=("Arial", 12), bg="white")
    total_label.pack(side=tk.LEFT, padx=10)

    tk.Button(bottom_frame, text="Generate Bill", bg="#27ae60", fg="white", font=("Arial", 10),
              padx=20, command=generate_bill).pack(side=tk.RIGHT, padx=10)
    tk.Button(bottom_frame, text="Clear", bg="#c0392b", fg="white", font=("Arial", 10),
              padx=20, command=clear_all).pack(side=tk.RIGHT, padx=5)
