from fpdf import FPDF
from utils.qr import generate_qr_code
import os
import datetime


def generate_pdf(bill_id, customer_name, customer_contact, customer_email, items, subtotal, tax_amount, total, tax_rate,payment,discount):
    pdf = FPDF()
    pdf.add_page()
    font_path = "fonts/"
    pdf.add_font('DejaVu', '',font_path+ 'DejaVuSansCondensed.ttf', uni=True)   # Regular
    pdf.add_font('DejaVu', 'B', font_path+'DejaVuSansCondensed-Bold.ttf', uni=True) # Bold

    pdf.set_font('DejaVu', '', 28)
    pdf.set_font('', 'B')
    pdf.cell(200, 10, txt="SHOPART", ln=True )
    pdf.set_font('', '')
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, txt="Leela Vihar Colony, Dholpur", ln=True, align='C')
    pdf.cell(200, 10, txt="Phone: +91 9875772746", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Bill No: {bill_id}", ln=True, align='C')
    pdf.ln(10)


    pdf.cell(200, 10, txt=f"Name: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Contact: {customer_contact}", ln=True)
    if customer_email != None:
        pdf.cell(200, 10, txt=f"Email: {customer_email}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Payment Mode: {payment}", ln=True)
    pdf.ln(10)

    pdf.cell(60, 10, "Product", border=1)
    pdf.cell(40, 10, "Price", border=1)
    pdf.cell(30, 10, "Quantity", border=1)
    pdf.cell(60, 10, "Total", border=1, ln=True)

    for item in items:
        pdf.cell(60, 10, item['name'], border=1)
        pdf.cell(40, 10, f"\u20b9{item['price']:.2f}", border=1)
        pdf.cell(30, 10, str(item['quantity']), border=1)
        pdf.cell(60, 10, f"\u20b9{item['total']:.2f}", border=1, ln=True)

    pdf.cell(130, 10, "SUBTOTAL:", border=1)
    pdf.cell(60, 10, f"\u20b9{subtotal:.2f}", border=1, ln=True)

    pdf.cell(130, 10, f"TAX ({int(tax_rate * 100)}%):", border=1)
    pdf.cell(60, 10, f"\u20b9{tax_amount:.2f}", border=1, ln=True)

    pdf.cell(130, 10, f"DISCOUNT ({discount}%):", border=1)
    pdf.cell(60, 10, f"\u20b9{subtotal * discount / 100}", border=1, ln=True)

    pdf.cell(130, 10, "GRAND TOTAL:", border=1)
    pdf.cell(60, 10, f"\u20b9{total:.2f}", border=1, ln=True)
    os.makedirs("bills", exist_ok=True)
    qr_path = generate_qr_code(f"bills/bill_{bill_id}.pdf", total)
    pdf.image(qr_path, x=160, y=pdf.get_y()+5, w=30)

    pdf.ln(10)
    pdf.cell(200, 10, txt="ShopArt", ln=True)

    pdf.ln(40)
    pdf.cell(200, 10, txt="Scan the QR to Pay", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Thank you {customer_name} for shopping with us !", ln=True, align='C')

    filename = f"bills/bill_{bill_id}.pdf"
    pdf.output(filename)

    if os.path.exists(qr_path):
        os.remove(qr_path)


    return filename
