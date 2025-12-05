"""
PDF Extraction Service
Extracts tables and text from PDF files and converts to JSON format
Includes OCR support for image-based PDFs
"""
import pdfplumber
import json
from typing import Dict, List, Any
import re
import os

# OCR imports
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not available. Install pytesseract and pdf2image for OCR support.")


# Configure Tesseract path (Windows)
# You may need to adjust this path based on your installation
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Public\Tesseract-OCR\tesseract.exe"
]

# Poppler paths for pdf2image (Windows)
# Download from: https://github.com/osber/pdf2image/releases or https://github.com/oschwartz10612/poppler-windows/releases
POPPLER_PATHS = [
    r"C:\Program Files\poppler\Library\bin",
    r"C:\Program Files\poppler-24.08.0\Library\bin",
    r"C:\poppler\Library\bin",
    r"C:\poppler\bin",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler", "Library", "bin"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler", "bin"),
]

POPPLER_PATH = None
for path in POPPLER_PATHS:
    if os.path.exists(path):
        POPPLER_PATH = path
        break

if OCR_AVAILABLE:
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


def try_ocr_extraction(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Attempt OCR extraction when normal extraction fails
    Converts PDF pages to images and uses Tesseract OCR
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of dictionaries containing OCR extracted data
    """
    if not OCR_AVAILABLE:
        print("OCR libraries not available. Install: pip install pytesseract pdf2image Pillow")
        return []
    
    all_data = []
    
    try:
        # Convert PDF to images (requires Poppler on Windows)
        if POPPLER_PATH:
            print(f"Using Poppler from: {POPPLER_PATH}")
            images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        else:
            # Try without explicit path (if Poppler is in system PATH)
            print("Poppler path not found, trying system PATH...")
            try:
                images = convert_from_path(pdf_path, dpi=300)
            except Exception as poppler_error:
                error_msg = str(poppler_error).lower()
                if 'poppler' in error_msg or 'pdftoppm' in error_msg:
                    print("\n" + "="*60)
                    print("ERROR: Poppler is not installed!")
                    print("="*60)
                    print("\nPoppler is required for OCR extraction on Windows.")
                    print("\nTo install Poppler:")
                    print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases")
                    print("2. Extract to C:\\poppler or C:\\Program Files\\poppler")
                    print("3. Add the 'bin' folder to your system PATH")
                    print("   OR place the 'poppler' folder in the ver-2 directory")
                    print("="*60 + "\n")
                raise poppler_error
        
        print(f"Converted PDF to {len(images)} images. Running OCR...")
        
        for page_num, image in enumerate(images, 1):
            print(f"  Processing page {page_num}...")
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            
            if text.strip():
                # Try to extract structured data from OCR text
                text_data = extract_key_value_from_text(text)
                
                if text_data:
                    text_data['page_number'] = page_num
                    text_data['content_type'] = 'ocr'
                    text_data['extraction_method'] = 'tesseract_ocr'
                    all_data.append(text_data)
                else:
                    # If no structured data, save raw text
                    all_data.append({
                        'page_number': page_num,
                        'content_type': 'ocr',
                        'extraction_method': 'tesseract_ocr',
                        'raw_text': text.strip()
                    })
    
    except Exception as e:
        error_msg = str(e)
        print(f"OCR extraction failed: {error_msg}")
        
        # Check for common issues
        if 'tesseract' in error_msg.lower():
            print("\nTesseract OCR is not installed or not in PATH.")
            print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        
        return []
    
    return all_data


def extract_tables_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract tables from PDF and return as list of dictionaries
    Uses OCR as fallback if normal extraction returns no data
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of dictionaries containing table data
    """
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract tables
            tables = page.extract_tables()
            
            if tables:
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:
                        # First row as headers
                        headers = [clean_text(cell) for cell in table[0] if cell]
                        
                        # Skip if no valid headers
                        if not headers:
                            continue
                        
                        # Process data rows
                        for row in table[1:]:
                            if row and any(cell for cell in row):  # Skip empty rows
                                row_data = {}
                                for idx, cell in enumerate(row):
                                    if idx < len(headers) and headers[idx]:
                                        row_data[headers[idx]] = clean_value(cell)
                                
                                if row_data:  # Only add non-empty rows
                                    row_data['page_number'] = page_num
                                    row_data['table_index'] = table_idx
                                    all_data.append(row_data)
            
            # If no tables found, extract text
            if not tables:
                text = page.extract_text()
                if text:
                    text_data = extract_key_value_from_text(text)
                    if text_data:
                        text_data['page_number'] = page_num
                        text_data['content_type'] = 'text'
                        all_data.append(text_data)
    
    # If no data extracted, try OCR
    if not all_data:
        print("Normal extraction returned no data. Attempting OCR...")
        all_data = try_ocr_extraction(pdf_path)
        
        if all_data:
            print(f"OCR extraction successful! Extracted {len(all_data)} records.")
        else:
            print("OCR extraction also failed or returned no data.")
    
    return all_data


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Replace problematic characters
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Create valid column name (alphanumeric and underscores only)
    text = re.sub(r'[^a-zA-Z0-9_\s]', '', text)
    text = text.replace(' ', '_').lower()
    
    return text


def clean_value(value: Any) -> Any:
    """Clean and convert value to appropriate type"""
    if value is None or value == '':
        return None
    
    if isinstance(value, str):
        value = value.strip()
        
        # Try to convert to number
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[,$₹]', '', value)
            if '.' in cleaned:
                return float(cleaned)
            return int(cleaned)
        except ValueError:
            return value
    
    return value


def extract_key_value_from_text(text: str) -> Dict[str, Any]:
    """
    Extract key-value pairs from unstructured text
    Simple pattern matching for common formats like "Key: Value"
    """
    data = {}
    lines = text.split('\n')
    
    for line in lines:
        # Match patterns like "Label: Value" or "Label - Value"
        match = re.match(r'^([^:]+?)[:：-]\s*(.+)$', line.strip())
        if match:
            key = clean_text(match.group(1))
            value = clean_value(match.group(2))
            if key:
                data[key] = value
    
    return data


def pdf_to_json(pdf_path: str) -> Dict[str, Any]:
    """
    Main function to convert PDF to JSON
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Dictionary containing extracted data and metadata
    """
    data = extract_tables_from_pdf(pdf_path)
    
    return {
        "success": True,
        "total_records": len(data),
        "data": data
    }
