import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv
from database.models import run_setup
from pages.login import login_page

# Load environment variables
load_dotenv()

# Setup the database and ensure all required tables exist
run_setup()

# Create root window
root = tk.Tk()
root.title("ShopArt Billing System")
root.geometry("1000x700")  # Ensure window size is big enough
root.configure(bg="white")

# Show login page
login_page(root)

# Start GUI loop
root.mainloop()
