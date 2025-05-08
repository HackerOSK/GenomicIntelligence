"""
PDF Processing Utility for extracting text from PDF files
"""

import os
import logging
from typing import Optional
import PyPDF2
from werkzeug.utils import secure_filename

# Configure logging
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file_stream) -> str:
    """
    Extract text content from a PDF file stream
    
    Args:
        pdf_file_stream: File-like object containing PDF data
        
    Returns:
        Extracted text content as a string
    """
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file_stream)
        
        # Get the number of pages
        num_pages = len(pdf_reader.pages)
        logger.info(f"Processing PDF with {num_pages} pages")
        
        # Extract text from each page
        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"Could not extract text from PDF: {str(e)}")

def save_uploaded_pdf(pdf_file, save_dir: str = "uploads") -> Optional[str]:
    """
    Save uploaded PDF file to disk
    
    Args:
        pdf_file: Flask FileStorage object
        save_dir: Directory to save the file
        
    Returns:
        Path to saved file or None if save failed
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate a secure filename
        filename = secure_filename(pdf_file.filename)
        
        # Create file path
        file_path = os.path.join(save_dir, filename)
        
        # Save the file
        pdf_file.save(file_path)
        logger.info(f"Saved PDF file to {file_path}")
        
        return file_path
    except Exception as e:
        logger.error(f"Error saving PDF file: {str(e)}")
        return None