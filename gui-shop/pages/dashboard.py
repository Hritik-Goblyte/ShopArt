import tkinter as tk
from pages.create_bill import create_bill
from pages.products import ProductManager
from pages.sales import show_sales
from pages.bills import show_bills
from pages.coupons import show_coupons
from pages.settings import show_settings
from pages.stock import show_stock
from pages.users import show_users


def check_coupon_expiry_reminder():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM discounts WHERE valid_until < datetime('now')")
    expired_count = c.fetchone()[0]

    if expired_count > 0:
        tk.Label(dashboard_frame, text="⚠️ Coupons expired! Generate new ones.", fg="red", bg="white", font=("Arial", 12, "bold")).pack(pady=5)


def show_products(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    screen = ProductManager(frame)
    screen.pack(fill="both", expand=True)

def show_home(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    welcome_frame = tk.Frame(frame, bg="white")
    welcome_frame.pack(expand=True)

    tk.Label(welcome_frame, text="👋 Welcome to", font=("Arial", 20), bg="white", fg="#2c3e50").pack(pady=10)
    tk.Label(welcome_frame, text="🛒 ShopArt Billing System", font=("Arial", 28, "bold"), bg="white", fg="#2980b9").pack(pady=10)
    tk.Label(welcome_frame, text="Select an option from the menu to get started.", font=("Arial", 12), bg="white", fg="gray").pack(pady=5)

def show_dashboard(root):
    for widget in root.winfo_children():
        widget.destroy()

    # Sidebar
    sidebar = tk.Frame(root, bg="#2c3e50", width=200)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)

    # Main Content
    content_frame = tk.Frame(root, bg="white")
    content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def menu_button(text, command):
        btn = tk.Button(sidebar, text=text, width=20, height=2, bg="#34495e", fg="white",
                        font=("Arial", 10), relief=tk.FLAT, command=command)
        btn.pack(pady=5, padx=10)

    tk.Label(sidebar, text="MENU", bg="#2c3e50", fg="white", font=("Arial", 14)).pack(pady=10)

    menu_button("🧾 Create Bill", lambda: create_bill(content_frame))
    menu_button("🗂 Bills", lambda: show_bills(content_frame))
    menu_button("📦 Products", lambda: show_products(content_frame))
    menu_button("🏬 Stocks", lambda: show_stock(content_frame))
    menu_button("📈 Sales", lambda: show_sales(content_frame))
    menu_button("🎟 Coupons", lambda: show_coupons(content_frame))
    menu_button("⚙ Settings", lambda: show_settings(content_frame))
    menu_button("👥 Users", lambda: show_users(content_frame))  # Optional: change if users page exists

    def logout():
        from pages.login import login_page
        login_page(root)

    tk.Button(sidebar, text="🚪 Logout", bg="#c0392b", fg="white", command=logout).pack(side=tk.BOTTOM, pady=10)

    # 👇 Load default home screen
    show_home(content_frame)
