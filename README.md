## 🧾 ShopArt - Billing & Inventory Management System

**ShopArt** is a complete GUI-based billing and inventory management system built with Python (Tkinter) and SQLite. It helps small shops manage sales, inventory, tax rates, UPI payments, and discount coupons efficiently with PDF invoice generation.

---

### 📦 Features

* 🔐 **Login & Registration** system
* 🧾 **Create Bills** with:

  * Customer Name, Contact, Email
  * Product selection by ID
  * Automatic subtotal, tax, discount
  * PDF Invoice generation with QR code
* 🛒 **Manage Products** (Add/Edit/Delete)
* 📈 **Sales History** and tracking
* 🎟 **Coupon Code System**

  * Generate 10 new coupons randomly
  * Email coupons to random customers
  * Valid for 1 week only
* ⚙️ **Settings Panel**

  * Change tax rate
  * Change UPI ID
  * Change admin password (with verification)
* 📬 **Email Integration**

  * Coupon codes are emailed using credentials stored securely in `.env`
* 🔄 **Auto-Expiry of Coupons**

  * Old coupons auto-deleted after expiry
  * Dashboard reminder for regeneration

---

### 🛠️ Tech Stack

* **Frontend:** Tkinter
* **Backend:** Python
* **Database:** SQLite
* **PDF Generation:** `fpdf`
* **Email:** `smtplib` with `.env` for secure credentials

---

### 📁 Project Structure

```
gui-shop/
│
├── main.py                    # Entry point
├── database/
│   ├── db.py                  # Connection helper
│   └── models.py              # DB schema & setup
│
├── pages/
│   ├── login.py
│   ├── dashboard.py
│   ├── billing.py
│   ├── products.py
│   ├── coupons.py
│   ├── settings.py
│
├── utils/
│   ├── common.py              # Password hash, settings helpers
│   ├── email_utils.py         # Coupon mailer
│   └── pdf_utils.py           # PDF generation
│
├── .env                       # Email + App Password (not tracked)
└── README.md                  # This file
```

---

### 📌 Prerequisites

* Python 3.8+
* Virtual environment (recommended)

---

### 🔧 Installation & Setup

```bash
# Clone the repo
git clone https://github.com/yourname/shopart
cd shopart/gui-shop

# Create and activate virtualenv
python3 -m venv myenv
source myenv/bin/activate

# Install required packages
pip install -r requirements.txt

# Create and populate .env file
touch .env
```


### 🚀 Run the App

```bash
python3 main.py
```

---

### 🧪 Manual DB Access (Optional)

```bash
sqlite3 database/shop.db
> SELECT * FROM discounts;
```

---

### 📮 TODO / Future Features

* Stock alert notification
* Export sales as CSV
* Barcode scanner support
* Dark mode UI

---
