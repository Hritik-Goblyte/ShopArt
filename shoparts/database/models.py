def setup_database(conn):
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 price REAL NOT NULL,
                 stock INTEGER DEFAULT 0)''')  # Add stock column
    
    # Create stock history table
    c.execute('''CREATE TABLE IF NOT EXISTS stock_history (
                 id INTEGER PRIMARY KEY,
                 product_id INTEGER NOT NULL,
                 change INTEGER NOT NULL,
                 reason TEXT NOT NULL,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(product_id) REFERENCES products(id))''')

                 
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY,
                customer_name TEXT NOT NULL,
                total REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                pdf_path TEXT NOT NULL,
                payment_mode TEXT NOT NULL DEFAULT 'Cash')''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL)''')

    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tax_rate', '0.05')")

    c.execute('''CREATE TABLE IF NOT EXISTS bill_items (
                bill_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY(bill_id) REFERENCES bills(id),
                FOREIGN KEY(product_id) REFERENCES products(id))''')


    c.execute('''CREATE TABLE IF NOT EXISTS discounts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 code TEXT UNIQUE NOT NULL,
                 discount INTEGER NOT NULL,
                 used INTEGER DEFAULT 0,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')


    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,       
            email TEXT UNIQUE,        -- Optional
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')





    

    conn.commit()