from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pathlib import Path


def generate_invoice_pdf(output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Invoice #INV-001", styles["Normal"]))
    elements.append(Paragraph("Date: 2026-02-01", styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Description Qty Unit Price Total", styles["Normal"]))
    elements.append(Paragraph("Widget A 2 100.00 200.00", styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Subtotal 200.00", styles["Normal"]))
    elements.append(Paragraph("Tax 20.00", styles["Normal"]))
    elements.append(Paragraph("Total 220.00", styles["Normal"]))

    doc.build(elements)