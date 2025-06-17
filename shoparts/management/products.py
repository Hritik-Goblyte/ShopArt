from tabulate import tabulate
import os
from utils.display import *

def add_product(conn):
    while True:
        print("\n--- Add New Product ---")
        name = input("Product Name: ")
        try:
            price = float(input("Price: "))
            stock = int(input("Initial Stock: "))
        except ValueError:
            print("\u274c Invalid price! Please enter a number.")
            continue

        c = conn.cursor()
        c.execute("INSERT INTO products (name, price,stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()

        product_id = c.lastrowid
        c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)", (product_id, stock, "Initial Stock"))
        conn.commit()

        print(f"\u2705 Product '{name}' added with {stock} units in stock successfully!")

        another = input("\nAdd another product? (y/n): ").strip().lower()
        if another != 'y':
            break

def list_products(conn, show_warnings=True):
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products")
    products = c.fetchall()

    if not products:
        print("No products found!")
        return

    low_stock_items = []
    for p in products:
        if p[3] < 5 and p[3] > 0:  # Low stock warning
            low_stock_items.append(p)
        elif p[3] <= 0:  # Out of stock warning
            low_stock_items.append(p)

    if show_warnings and low_stock_items:
        print("\n\u26A0 LOW STOCK WARNINGS:")
        for p in low_stock_items:
            status = "LOW" if p[3] > 0 else "OUT"
            print(f"- {p[1]}: {p[3]} units ({status})")


    print("\n--- Products List ---")
    print(tabulate(products, headers=["ID", "Name", "Price","Stock"], tablefmt="grid"))
    return products





def edit_product(conn):
    products = list_products(conn)
    if not products:
        return
    
    try:
        product_id = int(input("\nEnter Product ID to edit: "))
        
        # Verify product exists
        c = conn.cursor()
        c.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
        product = c.fetchone()
        
        if not product:
            print(f"\u274c Product ID {product_id} not found!")
            return
            
        print(f"\nEditing Product: {product[1]} (₹{product[2]:.2f})")
        
        # Get new values
        new_name = input(f"New name (current: {product[1]}, press Enter to keep): ").strip()
        new_price = input(f"New price (current: {product[2]:.2f}, press Enter to keep): ").strip()
        
        # Update values if provided
        update_fields = []
        update_values = []
        
        if new_name:
            update_fields.append("name = ?")
            update_values.append(new_name)
            
        if new_price:
            try:
                price_val = float(new_price)
                update_fields.append("price = ?")
                update_values.append(price_val)
            except ValueError:
                print("\u274c Invalid price! Update canceled.")
                return
                
        if not update_fields:
            print("ℹ️ No changes made.")
            return
            
        # Build and execute update query
        update_values.append(product_id)
        update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
        
        c.execute(update_query, update_values)
        conn.commit()
        
        print(f"\u2705 Product updated successfully!")
        
    except ValueError:
        print("\u274c Invalid input! Please enter a number.")




def delete_product(conn):
    products = list_products(conn)
    if not products:
        return
    
    try:
        product_id = int(input("\nEnter Product ID to delete: "))
        
        # Verify product exists
        c = conn.cursor()
        c.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
        product = c.fetchone()
        
        if not product:
            print(f"\u274c Product ID {product_id} not found!")
            return
            
        # Confirm deletion
        confirm = input(f"\n\u26A0 WARNING: Are you sure you want to delete '{product[1]}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion canceled.")
            return
            
        # Delete product
        c.execute("DELETE FROM products WHERE id = ?", (product_id,))
        c.execute("DELETE FROM stock_history WHERE product_id = ?", (product_id))
        conn.commit()
        print(f"\u2705 Product '{product[1]}' deleted successfully!")
        
    except ValueError:
        print("\u274c Invalid input! Please enter a number.")



def manage_stock(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    print_stock_ascii()
        
    products = list_products(conn)
    if not products:
        return
    
    try:
        product_id = int(input("\nEnter Product ID to manage stock: "))
        
        # Verify product exists
        c = conn.cursor()
        c.execute("SELECT id, name, stock FROM products WHERE id = ?", (product_id,))
        product = c.fetchone()
        
        if not product:
            print(f"\u274c Product ID {product_id} not found!")
            return
            
        print(f"\n--- Managing Stock for: {product[1]} ---")
        print(f"Current Stock: {product[2]}")
        
        # Get stock action
        print("\nStock Actions:")
        print("1. Add Stock")
        print("2. Remove Stock")
        print("3. View Stock History")
        action = input("\nSelect action: ")
        
        if action == '1':
            try:
                quantity = int(input("Quantity to add: "))
                if quantity <= 0:
                    print("\u274c Quantity must be positive!")
                    return
                    
                # Update stock
                new_stock = product[2] + quantity
                c.execute("UPDATE products SET stock = ? WHERE id = ?", 
                         (new_stock, product_id))
                
                # Record history
                c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)",
                         (product_id, quantity, "Stock addition"))
                
                conn.commit()
                print(f"\u2705 Added {quantity} units. New stock: {new_stock}")
                
            except ValueError:
                print("\u274c Invalid quantity!")
                
        elif action == '2':
            try:
                quantity = int(input("Quantity to remove: "))
                if quantity <= 0:
                    print("\u274c Quantity must be positive!")
                    return
                    
                if quantity > product[2]:
                    print("\u274c Cannot remove more than current stock!")
                    return
                    
                # Update stock
                new_stock = product[2] - quantity
                c.execute("UPDATE products SET stock = ? WHERE id = ?", 
                         (new_stock, product_id))
                
                # Record history
                c.execute("INSERT INTO stock_history (product_id, change, reason) VALUES (?, ?, ?)",
                         (product_id, -quantity, "Stock removal"))
                
                conn.commit()
                print(f"\u2705 Removed {quantity} units. New stock: {new_stock}")
                
            except ValueError:
                print("\u274c Invalid quantity!")
                
        elif action == '3':
            # View stock history
            c.execute("""
                SELECT timestamp, change, reason 
                FROM stock_history 
                WHERE product_id = ?
                ORDER BY timestamp DESC
            """, (product_id,))
            history = c.fetchall()
            
            if not history:
                print("\nNo stock history available.")
                return
                
            print(f"\n--- Stock History for: {product[1]} ---")
            print(tabulate(
                [(h[0], "+" + str(h[1]) if h[1] > 0 else h[1], h[2]) for h in history],
                headers=["Timestamp", "Change", "Reason"],
                tablefmt="grid"
            ))
            
        else:
            print("\u274c Invalid action selection!")
            
    except ValueError:
        print("\u274c Invalid input! Please enter a number.")




def stock_report(conn):
    c = conn.cursor()
    c.execute("""
        SELECT id, name, stock,
            CASE 
                WHEN stock <= 0 THEN '❌ Out of Stock'
                WHEN stock <= 5 THEN '⚠️ Low Stock'
                ELSE '✅ In Stock'
            END AS status
        FROM products
        ORDER BY stock ASC, name
    """)
    stock_data = c.fetchall()
    
    if not stock_data:
        print("No products found!")
        return
        
    print("\n--- STOCK REPORT ---")
    print(tabulate(
        [(item[0], item[1], item[2], item[3]) for item in stock_data],
        headers=["ID", "Product", "Stock", "Status"],
        tablefmt="grid"
    ))
    
    # Summary statistics
    c.execute("SELECT COUNT(*) FROM products WHERE stock <= 0")
    out_of_stock = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM products WHERE stock > 0 AND stock <= 5")
    low_stock = c.fetchone()[0]
    
    c.execute("SELECT SUM(stock * price) FROM products")
    inventory_value = c.fetchone()[0] or 0
    
    print("\n--- STOCK SUMMARY ---")
    print(f"• Out of Stock Items: {out_of_stock}")
    print(f"• Low Stock Items: {low_stock}")
    print(f"• Total Inventory Value: ₹{inventory_value:.2f}")