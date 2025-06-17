import os
from dotenv import load_dotenv

load_dotenv()

BANK_UPI = os.getenv("BANK_UPI", "test@upi")
PASSWORD = os.getenv("PASSWORD")