import qrcode
from config import BANK_UPI

def generate_qr_code(filename, amount):
    qr_data = f"upi://pay?pa={BANK_UPI}&pn=Shopart&am={amount:.2f}&cu=INR"
    qr = qrcode.make(qr_data)
    qr_path = filename.replace(".pdf", "_qr.png")
    qr.save(qr_path)
    return qr_path