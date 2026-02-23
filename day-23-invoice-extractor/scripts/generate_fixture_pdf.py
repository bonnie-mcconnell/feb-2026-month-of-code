from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib.units import inch

from pathlib import Path


def generate_invoice_pdf(output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Invoice #INV-001", styles["Normal"]))
    elements.append(Paragraph("Date: 2026-02-01", styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))

    data = [
        ["Description", "Qty", "Unit Price", "Total"],
        ["Widget A", "2", "100.00", "200.00"],
    ]

    table = Table(data)
    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ])
    )

    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph("Subtotal 200.00", styles["Normal"]))
    elements.append(Paragraph("Tax 20.00", styles["Normal"]))
    elements.append(Paragraph("Total 220.00", styles["Normal"]))

    doc.build(elements)


if __name__ == "__main__":
    generate_invoice_pdf(
        Path("invoice_extractor/tests/fixtures/sample_invoice_1.pdf")
    )