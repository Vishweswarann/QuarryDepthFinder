# [file name]: QuarryDepthFinder3/report_generator.py
import os
from datetime import datetime

from fpdf import FPDF


class QuarryReport(FPDF):
    def header(self):
        # Logo (if you have one, otherwise comment out)
        # self.image('static/Images/logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'QuarryDepthFinder Report', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_pdf_report(data, filename="report.pdf"):
    """
    Generates a PDF report for the quarry analysis.
    data: dict containing 'sitename', 'stats', 'image_path'
    """
    pdf = QuarryReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Site Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Site Analysis: {data.get('sitename', 'Unnamed Site')}", 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'L')
    pdf.ln(10)

    # 2. Statistics Section (Table-like)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "1. Excavation Statistics", 0, 1, 'L', 1)
    pdf.ln(5)

    stats = data.get('stats', {})
    
    # Helper to print a row
    def print_stat(label, value, unit=""):
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(60, 8, label, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f": {value} {unit}", 0, 1)

    print_stat("Max Depth", f"{stats.get('max_depth', 0):.2f}", "m")
    print_stat("Average Depth", f"{stats.get('mean_depth', 0):.2f}", "m")
    print_stat("Total Volume", f"{stats.get('volume_m3', 0):,.2f}", "m3")
    print_stat("Surface Area", f"{stats.get('total_area_m2', 0):,.2f}", "m2")
    print_stat("Min Elevation", f"{stats.get('min_elevation', 0):.2f}", "m")
    print_stat("Max Elevation", f"{stats.get('max_elevation', 0):.2f}", "m")
    
    pdf.ln(10)

    # 3. Visualization Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "2. Heatmap Visualization", 0, 1, 'L', 1)
    pdf.ln(5)

    image_path = data.get('image_path')
    if image_path and os.path.exists(image_path):
        # Center the image
        pdf.image(image_path, x=15, w=180)
    else:
        pdf.cell(0, 10, "No visualization image available.", 0, 1)

    # 4. Save
    output_path = os.path.join("static", "reports", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    
    return output_path
