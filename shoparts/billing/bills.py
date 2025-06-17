import datetime
import os
import subprocess
import sys
from tabulate import tabulate
from billing.pdf_generator import generate_pdf
from management.settings import get_tax_rate
from management.products import list_products
from utils.qr import generate_qr_code
from utils.sequence import get_next_bill_number  # Add this import
from utils.helpers import validate_date , add_user
from utils.display import print_create_ascii

def create_bill(conn):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_create_ascii()
        customer_name = input("Customer Name: ")
        customer_contact = input("Customer Phone: ")
        customer_email = input("Customer Email: ") or None

        items = []
        subtotal = 0.0

        list_products(conn)

        while True:
            try:
                product_input = input("\nEnter Product ID (0 to finish, -1 to show products): ")
                if product_input == '0':
                    break
                if product_input == '-1':
                    list_products(conn)
                    continue

                product_id = int(product_input)
                quantity = int(input("Quantity: "))

                c = conn.cursor()
                c.execute("SELECT id, name, price, stock FROM products WHERE id=?", (product_id,))
                product = c.fetchone()

                if not product:
                    print("\u274c Invalid Product ID!")
                    continue

                if product[3] < quantity:
                    print(f"\u274c Not Enough Stock! Only {product[3]} available.")
                    continue

                item_total = product[2] * quantity
                items.append({
                    'id': product[0],
                    'name': product[1],
                    'price': product[2],
                    'quantity': quantity,
                    'total': item_total
                })
                subtotal += item_total

                print(f"\u2795 Added {quantity} x {product[1]} = \u20b9{item_total:.2f}")

            except ValueError:
                print("\u274c Invalid input! Please enter numbers only.")

        if not items:
            print("\u274c No items added to bill!")
            another = input("\nTry to create this bill again? (y/n): ").strip().lower()
            if another != 'y':
                break
            else:
                continue

        tax_rate = get_tax_rate(conn)
        tax_amount = subtotal * tax_rate

        
        op = input("Is any Coupon Code available (y/n): ").strip().lower()

        if op == 'y':
            entered_code = input("Enter the coupon code: ").strip()

            c = conn.cursor()
            c.execute("SELECT discount FROM discounts WHERE used = 0 AND code = ?", (entered_code,))
            row = c.fetchone()

            if row:
                discount = row[0]
                print(f"Coupon applied! {discount}% discount.")
            else:
                print("Invalid or already used coupon.")
                discount = 0
        else:
            discount = 0

        # Calculate total
        total = subtotal + tax_amount

        if discount > 0:
            total = total - (subtotal * discount / 100)  # Applying percentage discount

        # print(f"Total amount after discount: {total}")

        
    
        payment1=input("1. Cash \n2.Online: ")
        if payment1 == '1': 
            payment = "Cash"
        elif payment1 == '2':
            payment = "Online"
        else:
            print("\u274c Invalid choice!")

        

        timestamp = datetime.datetime.now().isoformat()
        c = conn.cursor()
        c.execute("INSERT INTO bills (customer_name, total, payment_mode ,timestamp, pdf_path) VALUES (?, ?, ?, ? ,'')",
                  (customer_name, total,payment ,timestamp))
        bill_id = c.lastrowid
        
        pdf_path = generate_pdf(bill_id, customer_name, customer_contact, customer_email, items, subtotal, tax_amount, total, tax_rate,payment,discount)
        c.execute("UPDATE bills SET pdf_path=? WHERE id=?", (pdf_path, bill_id))

        for item in items:
            c.execute("INSERT INTO bill_items (bill_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                      (bill_id, item['id'], item['quantity'], item['price']))

        conn.commit()
        add_user(conn,customer_name,customer_contact,customer_email)
        print(f"\n\u2705 Bill created successfully! (ID: {bill_id})")
        print(f"\U0001F4C4 PDF saved at: {pdf_path}")  # Proper Unicode for 📄

        for item in items:
            product_id = int(item['id'])
            quantity = int(item['quantity'])

            # Debug info
            # print(f"Reducing stock: Product ID={product_id}, Quantity={quantity}")

            # Update stock
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))

            # Add to stock history
            c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)",
                    (product_id, -quantity, f"Bill #{bill_id}"))

            if op == 'y':
                c.execute("UPDATE discounts SET used = 1 WHERE code = ?" , (entered_code,))

        # Commit the changes
        conn.commit()

        another = input("\nCreate another bill? (y/n): ").strip().lower()
        if another != 'y':
            break






def list_today_bills(conn):
    c = conn.cursor()

    # Get today's date in format 'YYYY-MM-DD'
    today = datetime.date.today().isoformat()

    # Query bills from today only
    c.execute("SELECT id, customer_name, total, payment_mode, timestamp FROM bills WHERE DATE(timestamp) = ?", (today,))
    bills = c.fetchall()

    if not bills:
        print("📭 No bills found for today!")
        return

    print("\n🧾 --- Today's Bills ---")
    print(tabulate(
        [(i+1, bill[0], bill[1], f"\u20b9{bill[2]:.2f}", bill[3], bill[4]) for i, bill in enumerate(bills)],
        headers=["S.No.", "ID", "Customer", "Total", "Payment", "Timestamp"],
        tablefmt="grid"
    ))

    try:
        bill_input = input("\nEnter Bill ID to view (0 to exit): ")
        if bill_input == '0':
            return

        bill_id = int(bill_input)
        c.execute("SELECT pdf_path FROM bills WHERE id=?", (bill_id,))
        pdf_path = c.fetchone()

        if pdf_path:
            open_pdf(pdf_path[0])
        else:
            print("❌ Bill not found!")
    except ValueError:
        print("❌ Invalid input!")





def list_month_bills(conn):
    c = conn.cursor()

    # Get current year and month
    today = datetime.date.today()
    year = today.year
    month = today.month

    # Format: YYYY-MM
    month_str = f"{year:04d}-{month:02d}"

    # Query bills where timestamp starts with current year-month
    c.execute("SELECT id, customer_name, total, payment_mode, timestamp FROM bills WHERE strftime('%Y-%m', timestamp) = ?", (month_str,))
    bills = c.fetchall()

    if not bills:
        print("📭 No bills found for this month!")
        return

    print("\n📅 --- This Month's Bills ---")
    print(tabulate(
        [(i+1, bill[0], bill[1], f"\u20b9{bill[2]:.2f}", bill[3], bill[4]) for i, bill in enumerate(bills)],
        headers=["S.No.", "ID", "Customer", "Total", "Payment", "Timestamp"],
        tablefmt="grid"
    ))

    try:
        bill_input = input("\nEnter Bill ID to view (0 to exit): ")
        if bill_input == '0':
            return

        bill_id = int(bill_input)
        c.execute("SELECT pdf_path FROM bills WHERE id=?", (bill_id,))
        pdf_path = c.fetchone()

        if pdf_path:
            open_pdf(pdf_path[0])
        else:
            print("❌ Bill not found!")
    except ValueError:
        print("❌ Invalid input!")






def list_bills(conn):
    c = conn.cursor()
    c.execute("SELECT id, customer_name, total, payment_mode, timestamp FROM bills")
    bills = c.fetchall()

    if not bills:
        print("No bills found!")
        return

    print("\n--- Recent Bills ---")
    print(tabulate(
        [(i+1, bill[0], bill[1], f"\u20b9{bill[2]:.2f}", bill[3], bill[4]) for i, bill in enumerate(bills)],
        headers=["S.No", "ID", "Customer", "Total", "Payment", "Timestamp"],
        tablefmt="grid"
    ))

    try:
        bill_input = input("\nEnter Bill ID to view (0 to exit): ")
        if bill_input == '0':
            return

        bill_id = int(bill_input)
        c.execute("SELECT pdf_path FROM bills WHERE id=?", (bill_id,))
        pdf_path = c.fetchone()

        if pdf_path:
            open_pdf(pdf_path[0])
        else:
            print("\u274c Bill not found!")
    except ValueError:
        print("\u274c Invalid input!")





def list_custom_bills(conn):
    print("\n--- Bills by Date Range ---")
    
    try:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        
        # Validate dates
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        c = conn.cursor()
        c.execute("""
            SELECT id, customer_name, total, payment_mode, timestamp 
            FROM bills 
            WHERE DATE(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp
        """, (start_date, end_date))
        
        bills = c.fetchall()
        
        if not bills:
            print(f"\n📭 No bills found between {start_date} and {end_date}!")
            return
            
        print(f"\n📅 Bills from {start_date} to {end_date}:")
        print(tabulate(
            [(i+1, bill[0], bill[1], f"₹{bill[2]:.2f}", bill[3], bill[4]) for i, bill in enumerate(bills)],
            headers=["S.No.", "Bill No.", "Customer", "Total", "Payment", "Timestamp"],
            tablefmt="grid"
        ))
        
        bill_input = input("\nEnter Bill Number to view (0 to exit): ")
        if bill_input == '0':
            return
            
        # Validate bill number format
        if not (bill_input.startswith('SA') and bill_input[2:].isdigit()):
            print("❌ Invalid bill number format! Should be SA followed by numbers.")
            return
            
        c.execute("SELECT pdf_path FROM bills WHERE id = ?", (bill_input,))
        pdf_path = c.fetchone()
        
        if pdf_path:
            open_pdf(pdf_path[0])
        else:
            print("❌ Bill not found!")
            
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        if "does not match format" in str(e):
            print("❗ Please enter dates in YYYY-MM-DD format")




def list_bills_by_date(conn):
    """List all bills for a specific date"""
    print("\n--- Bills for Specific Date ---")
    
    try:
        # Get date input and validate format
        date_str = input("Enter date (YYYY-MM-DD): ")
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        c = conn.cursor()
        c.execute("""
            SELECT id, customer_name, total, payment_mode, timestamp 
            FROM bills 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp
        """, (date_str,))
        
        bills = c.fetchall()
        
        if not bills:
            print(f"\n📭 No bills found on {date_str}!")
            return
            
        print(f"\n📅 Bills for {date_str}:")
        print(tabulate(
            [(i+1, bill[0], bill[1], f"₹{bill[2]:.2f}", bill[3], bill[4]) for i, bill in enumerate(bills)],
            headers=["S.No.", "Bill No.", "Customer", "Total", "Payment", "Timestamp"],
            tablefmt="grid"
        ))
        
        bill_input = input("\nEnter Bill Number to view (0 to exit): ")
        if bill_input == '0':
            return
            
        # Validate bill number format
        if not (bill_input.startswith('SA') and bill_input[2:].isdigit()):
            print("❌ Invalid bill number format! Should be SA followed by numbers.")
            return
            
        c.execute("SELECT pdf_path FROM bills WHERE id = ?", (bill_input,))
        pdf_path = c.fetchone()
        
        if pdf_path:
            open_pdf(pdf_path[0])
        else:
            print("❌ Bill not found!")
            
    except ValueError:
        print("❌ Invalid date format! Please use YYYY-MM-DD format.")






# def open_pdf(pdf_path):
#     # PDF opening code
#     # ... [rest of open_pdf code] ...

def open_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print("\u274c PDF file not found!")
        return
    try:
        if os.name == 'nt':
            os.startfile(pdf_path)
        elif os.name == 'posix':
            subprocess.run(['open', pdf_path] if sys.platform == 'darwin' else ['xdg-open', pdf_path])
        print(f"\ud83d\udcc4 Opening PDF: {pdf_path}")
    except Exception as e:
        print(f"\u274c Could not open PDF: {e}")
