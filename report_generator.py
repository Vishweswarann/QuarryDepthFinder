# [file name]: report_generator.py
# [file content begin]
import os
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from fpdf import FPDF
from datetime import datetime
from depth_analysis import calculate_quarry_depth
from volume_calculator import calculate_excavation_volume
from slope_analysis import analyze_slope_contours

class QuarryReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Quarry Analysis Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, body)
        self.ln()

def generate_quarry_report(quarry_name, dem_file, output_dir="static/reports"):
    """
    Generate comprehensive PDF report for quarry analysis
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate analysis data
    depth_data, depth_stats, transform, crs = calculate_quarry_depth(dem_file)
    volume_data = calculate_excavation_volume(dem_file)
    slope_data = analyze_slope_contours(dem_file)
    
    # Create visualizations
    viz_files = create_report_visualizations(dem_file, depth_data, slope_data, output_dir)
    
    # Generate PDF
    pdf = QuarryReportPDF()
    pdf.add_page()
    
    # Title page
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, f'QUARRY ANALYSIS REPORT', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Site: {quarry_name}', 0, 1, 'C')
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.ln(20)
    
    # Executive Summary
    pdf.chapter_title('EXECUTIVE SUMMARY')
    summary = f"""
    This report provides a comprehensive analysis of the quarry site '{quarry_name}'. 
    The analysis includes depth measurements, volume calculations, slope analysis, 
    and safety recommendations based on digital elevation model data.
    
    Key Findings:
    - Maximum Depth: {depth_stats['max_depth']:.1f} meters
    - Total Excavation Volume: {volume_data['volume_pixel_method_m3']:,.0f} cubic meters
    - Quarry Area: {depth_stats['total_area_m2']:,.0f} square meters
    - Average Depth: {depth_stats['mean_depth']:.1f} meters
    """
    pdf.chapter_body(summary)
    
    # Depth Analysis
    pdf.add_page()
    pdf.chapter_title('DEPTH ANALYSIS')
    pdf.chapter_body(f"""
    Depth analysis reveals the excavation characteristics of the quarry:
    
    Maximum Depth: {depth_stats['max_depth']:.1f} meters
    Minimum Depth: {depth_stats['min_depth']:.1f} meters  
    Average Depth: {depth_stats['mean_depth']:.1f} meters
    Total Volume: {depth_stats['volume_m3']:,.0f} cubic meters
    Surface Area: {depth_stats['total_area_m2']:,.0f} square meters
    """)
    
    # Add depth visualization
    if viz_files['depth']:
        pdf.image(viz_files['depth'], x=10, y=100, w=180)
    
    # Volume Analysis
    pdf.add_page()
    pdf.chapter_title('VOLUME ANALYSIS')
    
    volume_text = f"""
    Excavation Volume Calculation:
    
    Pixel-based Method: {volume_data['volume_pixel_method_m3']:,.0f} m³
    Integration Method: {volume_data['volume_integral_method_m3']:,.0f} m³
    Excavation Area: {volume_data['excavation_area_m2']:,.0f} m²
    
    Material Categories:
    """
    pdf.chapter_body(volume_text)
    
    # Material categories table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 8, 'Depth Category', 1)
    pdf.cell(40, 8, 'Volume (m³)', 1)
    pdf.cell(40, 8, 'Area (m²)', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    for category, data in volume_data['material_categories'].items():
        category_name = category.replace('_', ' ').title()
        pdf.cell(60, 8, category_name, 1)
        pdf.cell(40, 8, f"{data['volume_m3']:,.0f}", 1)
        pdf.cell(40, 8, f"{data['area_m2']:,.0f}", 1)
        pdf.ln()
    
    # Slope Analysis
    pdf.add_page()
    pdf.chapter_title('SLOPE ANALYSIS')
    pdf.chapter_body(f"""
    Slope analysis provides insights into terrain stability and safety:
    
    Average Slope: {slope_data['average_slope_degrees']:.1f}°
    Maximum Slope: {slope_data['max_slope_degrees']:.1f}°
    Slope Variability: {slope_data['slope_std']:.1f}°
    
    Safety zones identified based on slope thresholds.
    """)
    
    if viz_files['slope']:
        pdf.image(viz_files['slope'], x=10, y=80, w=180)
    
    # Recommendations
    pdf.add_page()
    pdf.chapter_title('RECOMMENDATIONS')
    recommendations = generate_recommendations(depth_stats, slope_data, volume_data)
    pdf.chapter_body(recommendations)
    
    # Save PDF
    report_filename = f"quarry_report_{quarry_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    report_path = os.path.join(output_dir, report_filename)
    pdf.output(report_path)
    
    return report_path

def create_report_visualizations(dem_file, depth_data, slope_data, output_dir):
    """Create visualization images for the report"""
    viz_files = {}
    
    # Depth visualization
    plt.figure(figsize=(10, 8))
    plt.imshow(depth_data, cmap='viridis')
    plt.colorbar(label='Depth (meters)')
    plt.title('Quarry Depth Analysis')
    depth_viz_path = os.path.join(output_dir, 'depth_analysis.png')
    plt.savefig(depth_viz_path, dpi=150, bbox_inches='tight')
    plt.close()
    viz_files['depth'] = depth_viz_path
    
    # Slope visualization
    plt.figure(figsize=(10, 8))
    plt.imshow(slope_data['slope_map'], cmap='hot')
    plt.colorbar(label='Slope (degrees)')
    plt.title('Slope Analysis')
    slope_viz_path = os.path.join(output_dir, 'slope_analysis.png')
    plt.savefig(slope_viz_path, dpi=150, bbox_inches='tight')
    plt.close()
    viz_files['slope'] = slope_viz_path
    
    return viz_files

def generate_recommendations(depth_stats, slope_data, volume_data):
    """Generate safety and operational recommendations"""
    recommendations = []
    
    # Depth-based recommendations
    max_depth = depth_stats['max_depth']
    if max_depth > 50:
        recommendations.append("⚠️  CRITICAL: Depth exceeds 50m - Implement enhanced safety monitoring")
    elif max_depth > 30:
        recommendations.append("⚠️  WARNING: Depth exceeds 30m - Regular slope stability checks required")
    else:
        recommendations.append("✅  Depth within safe operational limits")
    
    # Slope-based recommendations
    max_slope = slope_data['max_slope_degrees']
    if max_slope > 45:
        recommendations.append("⚠️  CRITICAL: Maximum slope exceeds 45° - High risk of slope failure")
    elif max_slope > 35:
        recommendations.append("⚠️  WARNING: Maximum slope exceeds 35° - Implement slope monitoring")
    else:
        recommendations.append("✅  Slope angles within safe operational range")
    
    # Volume-based recommendations
    total_volume = volume_data['volume_pixel_method_m3']
    if total_volume > 1_000_000:
        recommendations.append("📊  Large-scale operation: Consider phased excavation plan")
    elif total_volume > 100_000:
        recommendations.append("📊  Medium-scale operation: Optimize extraction sequencing")
    else:
        recommendations.append("📊  Small-scale operation: Suitable for localized extraction")
    
    # Operational recommendations
    recommendations.extend([
        "\nOPERATIONAL RECOMMENDATIONS:",
        "• Conduct regular drone surveys for updated volume calculations",
        "• Implement slope monitoring systems in high-risk areas", 
        "• Develop water drainage plan for monsoon season",
        "• Establish safety zones around steep slopes",
        "• Regular equipment maintenance for excavation efficiency"
    ])
    
    return "\n".join(recommendations)
# [file content end]