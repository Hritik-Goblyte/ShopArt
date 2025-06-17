import qrcode
import os
from dotenv import load_dotenv
load_dotenv()
from utils.common import get_setting

BANK_UPI = get_setting("bank_upi")

def generate_qr_code(filename, amount):
    qr_data = f"upi://pay?pa={BANK_UPI}&pn=Shopart&am={amount:.2f}&cu=INR"
    qr = qrcode.make(qr_data)
    qr_path = filename.replace(".pdf", "_qr.png")
    qr.save(qr_path)
    return qr_path