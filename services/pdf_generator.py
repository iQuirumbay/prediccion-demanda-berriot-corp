# services/pdf_generator.py
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
import io


def generate_pdf(requisitions_df):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4
    )

    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("ORDENES DE REQUISICIÓN SUGERIDAS", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Tabla
    data = [requisitions_df.columns.tolist()] + requisitions_df.values.tolist()

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#B45309")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return buffer