"""
PDF Generator for therapy reports
"""

import os
import logging
import datetime
from typing import Dict, Any, List
from fpdf import FPDF

# Configure logging
logger = logging.getLogger(__name__)

class TherapyReportPDF(FPDF):
    """Custom PDF class for therapy reports"""
    
    def __init__(self):
        # Initialize FPDF with standard parameters 
        FPDF.__init__(self, orientation='P', unit='mm', format='A4')
        # We'll use core fonts and replace unicode characters with ASCII equivalents
    
    def header(self):
        """Add header to each page"""
        # Set font
        self.set_font('Arial', 'B', 12)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Precision Medicine Assistant - Therapy Report', 0, 0, 'C')
        # Line break
        self.ln(20)
    
    def footer(self):
        """Add footer to each page"""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        # Date
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cell(0, 10, f'Generated on {today}', 0, 0, 'R')
        
    def safe_cell(self, w, h, txt, border=0, ln=0, align='', fill=False):
        """Cell method that safely handles Unicode characters"""
        # Replace Unicode characters with ASCII equivalents
        safe_txt = txt.replace('•', '*').replace('–', '-').replace('…', '...').encode('latin-1', 'replace').decode('latin-1')
        # Ensure border is 0 or 1
        border_val = 0 if border == 0 else 1
        self.cell(w, h, safe_txt, border_val, ln, align, fill)
        
    def safe_multi_cell(self, w, h, txt, border=0, align='', fill=False):
        """Multi_cell method that safely handles Unicode characters"""
        # Replace Unicode characters with ASCII equivalents
        safe_txt = txt.replace('•', '*').replace('–', '-').replace('…', '...').encode('latin-1', 'replace').decode('latin-1')
        # Ensure border is 0 or 1
        border_val = 0 if border == 0 else 1
        self.multi_cell(w, h, safe_txt, border_val, align, fill)

def generate_therapy_report(
    profile: Dict[str, Any],
    entities: Dict[str, Any],
    therapies: List[Dict[str, Any]],
    agent_type: str,
    query: str,
    output_path: str
) -> str:
    """
    Generate a PDF report of therapy recommendations
    
    Args:
        profile: User profile data
        entities: Extracted medical entities
        therapies: List of therapy recommendations
        agent_type: Type of agent used (allopathy, homeopathy, or both)
        query: User's query
        output_path: Directory to save the PDF
        
    Returns:
        Path to the generated PDF file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Create PDF object
        pdf = TherapyReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Set font
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.safe_cell(0, 10, 'Therapy Recommendations Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Agent type
        pdf.set_font('Arial', 'B', 12)
        agent_heading = {
            'allopathy': 'Allopathic Medicine Recommendations',
            'homeopathy': 'Homeopathic Medicine Recommendations',
            'ayurveda': 'Ayurvedic Medicine Recommendations',
            'both': 'Integrated Medicine Recommendations (Allopathy & Homeopathy)',
            'all': 'Holistic Medicine Recommendations (All Approaches)'
        }.get(agent_type, 'Medicine Recommendations')
        
        pdf.safe_cell(0, 10, agent_heading, 0, 1, 'L')
        pdf.ln(5)
        
        # User query
        pdf.set_font('Arial', 'B', 11)
        pdf.safe_cell(0, 10, 'Your Health Query:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.safe_multi_cell(0, 10, query)
        pdf.ln(5)
        
        # Patient Information Section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Patient Information', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        if profile:
            info_items = [
                ('Age', profile.get('age', 'Not specified')),
                ('Gender', profile.get('gender', 'Not specified')),
                ('Height', profile.get('height', 'Not specified')),
                ('Weight', profile.get('weight', 'Not specified')),
                ('Lifestyle', profile.get('lifestyle', 'Not specified')),
                ('Medical History', profile.get('medical_history', 'Not specified')),
                ('Allergies', profile.get('allergies', 'Not specified')),
                ('Current Medications', profile.get('current_medications', 'Not specified'))
            ]
            
            for label, value in info_items:
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(40, 10, f"{label}:", 0, 0)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 10, str(value))
        else:
            pdf.cell(0, 10, 'No profile information available', 0, 1)
        
        pdf.ln(5)
        
        # Medical Entities Section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Extracted Medical Entities', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        if entities:
            entity_categories = [
                ('Diseases', entities.get('diseases', [])),
                ('Symptoms', entities.get('symptoms', [])),
                ('Lab Values', entities.get('lab_values', [])),
                ('Genes', entities.get('genes', [])),
                ('Medications', entities.get('medications', []))
            ]
            
            for category, items in entity_categories:
                if items:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 10, f"{category}:", 0, 1)
                    pdf.set_font('Arial', '', 10)
                    
                    if isinstance(items[0], dict):
                        # For lab values or other structured data
                        for item in items:
                            if 'name' in item and 'value' in item:
                                unit_str = f" {item.get('unit', '')}" if 'unit' in item else ""
                                pdf.safe_cell(0, 10, f"* {item['name']}: {item['value']}{unit_str}", 0, 1)
                    else:
                        # For simple string lists
                        for item in items:
                            pdf.safe_cell(0, 10, f"* {item}", 0, 1)
                    pdf.ln(2)
        else:
            pdf.cell(0, 10, 'No medical entities extracted', 0, 1)
        
        pdf.ln(5)
        
        # Therapy Recommendations Section
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'Therapy Recommendations', 0, 1, 'C')
        pdf.ln(5)
        
        # Add each therapy
        for idx, therapy in enumerate(therapies):
            pdf.set_font('Arial', 'B', 12)
            therapy_type = therapy.get('therapy_type', 'Unknown')
            therapy_name = therapy.get('therapy_name', 'Unknown Therapy')
            pdf.safe_cell(0, 10, f"{idx+1}. {therapy_name} ({therapy_type.capitalize()})", 0, 1, 'L')
            pdf.ln(2)
            
            pdf.set_font('Arial', 'B', 10)
            pdf.safe_cell(40, 10, "Description:", 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.safe_multi_cell(0, 10, therapy.get('description', 'No description available'))
            
            # Scores section
            pdf.set_font('Arial', 'B', 11)
            pdf.safe_cell(0, 10, "Scores:", 0, 1)
            
            scores = [
                ('Efficacy', therapy.get('efficacy_score', 'N/A')),
                ('Compatibility', therapy.get('compatibility_score', 'N/A')),
                ('Safety', therapy.get('safety_score', 'N/A')),
                ('Cost', therapy.get('cost_score', 'N/A')),
                ('Overall', therapy.get('overall_score', 'N/A'))
            ]
            
            for score_name, score_value in scores:
                pdf.set_font('Arial', 'B', 10)
                pdf.safe_cell(40, 10, f"{score_name}:", 0, 0)
                pdf.set_font('Arial', '', 10)
                pdf.safe_cell(0, 10, f"{score_value}/100", 0, 1)
            
            # Side effects
            pdf.set_font('Arial', 'B', 10)
            pdf.safe_cell(40, 10, "Side Effects:", 0, 0)
            pdf.set_font('Arial', '', 10)
            
            side_effects = therapy.get('side_effects', [])
            if side_effects:
                if isinstance(side_effects, list):
                    pdf.safe_multi_cell(0, 10, ", ".join(side_effects))
                else:
                    pdf.safe_multi_cell(0, 10, str(side_effects))
            else:
                pdf.safe_multi_cell(0, 10, "None reported")
            
            # Contraindications
            pdf.set_font('Arial', 'B', 10)
            pdf.safe_cell(40, 10, "Contraindications:", 0, 0)
            pdf.set_font('Arial', '', 10)
            
            contraindications = therapy.get('contraindications', [])
            if contraindications:
                if isinstance(contraindications, list):
                    pdf.safe_multi_cell(0, 10, ", ".join(contraindications))
                else:
                    pdf.safe_multi_cell(0, 10, str(contraindications))
            else:
                pdf.safe_multi_cell(0, 10, "None reported")
            
            # Supporting evidence
            pdf.set_font('Arial', 'B', 10)
            pdf.safe_cell(40, 10, "Evidence:", 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.safe_multi_cell(0, 10, therapy.get('supporting_evidence', 'No evidence data available'))
            
            # Add space between therapies
            pdf.ln(10)
            
            # Add a line between therapies if not the last one
            if idx < len(therapies) - 1:
                pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                pdf.ln(10)
        
        # Disclaimer
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.safe_cell(0, 10, 'Important Disclaimer', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        disclaimer_text = """
        This report is generated by an AI-powered Precision Medicine Assistant and is intended for informational purposes only. The recommendations provided are based on the information available and should not be considered as medical advice.

        Always consult with a qualified healthcare professional before making any decisions about your health or treatment. The AI system does not replace professional medical advice, diagnosis, or treatment.

        The efficacy, safety, and compatibility scores are estimates based on available data and should be validated by healthcare professionals. Individual responses to treatments may vary.
        """
        pdf.safe_multi_cell(0, 10, disclaimer_text.strip())
        
        # Final timestamp
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 10)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.safe_cell(0, 10, f"Report generated on: {timestamp}", 0, 1, 'R')
        
        # Generate filename
        timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"therapy_report_{timestamp_str}.pdf"
        filepath = os.path.join(output_path, filename)
        
        # Save the PDF
        pdf.output(filepath)
        logger.info(f"Generated therapy report: {filepath}")
        
        return filepath
    
    except Exception as e:
        logger.error(f"Error generating therapy report PDF: {str(e)}")
        raise ValueError(f"Could not generate PDF report: {str(e)}")