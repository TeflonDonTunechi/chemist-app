from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime

def generate_receipt(sale_id, items, total, cashier_name, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.3, 0.2, 0.6)  # purple
    c.drawString(2*cm, height-2*cm, "Zeitgeist Teflon Pharma")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(2*cm, height-2.7*cm, "Your Trusted Pharmacy")
    c.drawString(2*cm, height-3.4*cm, f"Sale ID: {sale_id}")
    c.drawString(2*cm, height-3.9*cm, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(2*cm, height-4.4*cm, f"Cashier: {cashier_name}")
    
    y = height - 5.5*cm
    
    # Table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Item")
    c.drawString(8*cm, y, "Qty")
    c.drawString(10*cm, y, "Price (KES)")
    c.drawString(14*cm, y, "Subtotal")
    y -= 0.5*cm
    c.line(2*cm, y, 18*cm, y)
    y -= 0.5*cm
    
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(2*cm, y, item['name'][:30])
        c.drawString(8*cm, y, str(item['qty']))
        c.drawString(10*cm, y, f"{item['price']:.2f}")
        c.drawString(14*cm, y, f"{item['subtotal']:.2f}")
        y -= 0.5*cm
        if y < 5*cm:
            c.showPage()
            y = height - 2*cm
            c.setFont("Helvetica", 10)
    
    # Total
    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10*cm, y, f"TOTAL: KES {total:.2f}")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, 2*cm, "Thank you for your business!")
    c.drawString(2*cm, 1.5*cm, "Zeitgeist Teflon Pharma © 2026")
    
    c.save()
    return output_path