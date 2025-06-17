import os
import sqlite3      # For SQLite database connection
import datetime     # For handling date and time
from database.db import get_connection
from database.models import setup_database
from utils.auth import login
from utils.display import *
from utils.coupons import *
from management.products import *
from management.settings import *
from billing.bills import *
from sales.sales import *

def main_menu(conn):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_ascii_art()
        print("\n MAIN MENU \n")
        print("1. Create Bills")
        print("2. Bills")
        print("3. Sales")
        print("4. Products.")
        print("5. Settings")
        print("6. Coupon Code")
        print("7. Log-Out")

        try:
            choice = input("\nEnter your choice: ")

            if choice == '1':
                create_bill(conn)
            elif choice == '2':
                bills_menu(conn)
            elif choice == '3':
                sales_menu(conn)
            elif choice == '4':
                management_menu(conn)
            elif choice == '5':
                setting_menu(conn)
            elif choice == '6':
                generate_daily_coupons(conn)
            elif choice == '7':
                print("\nThank you for using Shop Bill Manager!")
                break
            else:
                print("\u274c Invalid choice! Please try again.")

            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')

        except KeyboardInterrupt:
            print("\n\nExiting program...")
            break

#2.
def bills_menu(conn):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_bills_ascii()
        print("\n--- View Bills ---")
        print("1. Today Bills")
        print("2. This Month Bills")
        print("3. Custom Dates")
        print("4. Specific Date")
        print("5. All Bills")
        print("6. Back to Main Menu")

        sub_choice = input("\nEnter the Choice: ")
        if sub_choice == '1':
            list_today_bills(conn)
        elif sub_choice == '2':
            list_month_bills(conn)
        elif sub_choice == '3':
            list_custom_bills(conn)
        elif sub_choice == '4':
            list_bills_by_date(conn)
        elif sub_choice == '5':
            list_bills(conn)
        elif sub_choice == '6':
            break
        else:
            print("\u274c Invalid choice!")


#3.
def sales_menu(conn):
    # write codes to see this moth sales , custom dates slaes (from - to),specific dates sale,total sales(this year and last year but in different lines)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_sales_ascii()
        print("\n--- SALES ---")
        print("1. Today's Sales")
        print("2. This Month Sales")
        print("3. Custom Dates")
        print("4. Specific Date")
        print("5. Total Sales")
        print("6. Back to Main Menu")

        sub_choice = input("\nEnter the Choice: ")
        if sub_choice == '1':
            today_sales(conn)
            input("\nPress Enter to Continue")
        elif sub_choice == '2':
            today = datetime.date.today()
            sales = get_monthly_sales(conn, today.year, today.month)
            print(f"\n📊 This Month's Sales ({today.strftime('%B %Y')}): ₹{sales:.2f}")
            input("\nPress Enter to Continue")
        elif sub_choice == '3':
            try:
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
                
                sales = get_range_sales(conn, start_date, end_date)
                print(f"\n📊 Total Sales from {start_date} to {end_date}: ₹{sales:.2f}")
                input("\nPress Enter to Continue")
                
            except ValueError:
                print("❌ Invalid date format! Please use YYYY-MM-DD")
                input("\nPress Enter to Continue")
        elif sub_choice == '4':
            try:
                date = input("Enter date (YYYY-MM-DD): ")
                datetime.datetime.strptime(date, '%Y-%m-%d')
                
                sales = get_daily_sales(conn, date)
                print(f"\n📊 Sales on {date}: ₹{sales:.2f}")
                input("\nPress Enter to Continue")
                
            except ValueError:
                print("❌ Invalid date format! Please use YYYY-MM-DD")
                input("\nPress Enter to Continue")
        elif sub_choice == '5':
            current_year = datetime.date.today().year
            last_year = current_year - 1
            
            current_sales = get_yearly_sales(conn, current_year)
            last_sales = get_yearly_sales(conn, last_year)
            
            print("\n--- YEARLY SALES COMPARISON ---")
            print(f"📊 {last_year} Total Sales: ₹{last_sales:.2f}")
            print(f"📊 {current_year} Total Sales: ₹{current_sales:.2f}")

            
            if last_sales > 0:
                growth = ((current_sales - last_sales) / last_sales) * 100
                print(f"📈 YoY Growth: {growth:.2f}%")
                input("\nPress Enter to Continue")
            else:
                print("📈 YoY Growth: N/A (No previous year data)")
                input("\nPress Enter to Continue")
        elif sub_choice == '6':
            break
        else:
            print("\u274c Invalid choice!")



#4
def management_menu(conn):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_product_ascii()
        print("\n--- PRODUCT MANAGEMENT ---")
        print("1. Add Product")
        print("2. List Products")
        print("3. Edit Products")
        print("4. Delete Products")
        print("5. Stocks")
        print("6. Stock Report")
        print("7. Back to Main Menu")

        sub_choice = input("\nEnter choice: ")
        if sub_choice == '1':
            add_product(conn)
        elif sub_choice == '2':
            list_products(conn)
        elif sub_choice == '3':
            edit_product(conn)
        elif sub_choice == '4':
            delete_product(conn)
        elif sub_choice == '5':
            manage_stock(conn)
        elif sub_choice == '6':
            stock_report(conn)
        elif sub_choice == '7':
            break
        else:
            print("\u274c Invalid choice!")

        input("\nPress Enter to continue...")
        





#5.
def setting_menu(conn):
    # 

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        # print("\n--- SETTINGS ---")
        print_settings_ascii()
        print("1. Change Tax Rate")
        print("2. Change Password")
        print("3. Back to Main Menu")

        sub_choice = input("\nEnter choice: ")
        if sub_choice == '1':
            if login():
                try:
                    tax = get_tax_rate(conn)
                    print(f"The Current Tax Rate is {tax*100}%")
                    new_rate = float(input("Enter new tax rate in % (e.g., 18 for 18%): ")) / 100
                    if new_rate < 0 or new_rate > 1:
                        print("❌ Invalid tax rate! Must be between 0% and 100%")
                    else:
                        set_tax_rate(conn, new_rate)
                except ValueError:
                    print("❌ Invalid input!")

        elif sub_choice == '2':
            if login():
                try:
                    new_pass = input("Enter the New Password: ")
                    update_password('../.env', new_pass)
                    print("✅ Password Changed Successfully.")
                except ValueError:
                    print("❌ Invalid input!")


        elif sub_choice == '3':
            break
        else:
            print("\u274c Invalid choice!")

        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')





def main():
    conn = get_connection()
    setup_database(conn)
    
    if login():
        main_menu(conn)
    conn.close()

if __name__ == "__main__":
    main()