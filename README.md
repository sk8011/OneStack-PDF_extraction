# PDF Data Extraction and Storage System

A Python system that extracts structured data from PDF files (invoices, balance sheets, financial reports) and stores them in a database with auto-generated schema.

![alt text](image.png)

## Features

- Upload PDF files through web interface or API
- Extract tables from text-based PDFs using pdfplumber
- Extract data from image-based/scanned PDFs using OCR (Tesseract)
- Automatically create database tables based on extracted data
- Add new columns when new data fields appear
- View, edit, add, and delete records through web interface
- Export data to Excel files


## Requirements

- Python 3.8 or higher
- Tesseract OCR (optional, for image-based PDFs)
- Poppler (optional, required for OCR to convert PDF to images)


## Quick Start

Step 1: Install Python dependencies
```
pip install -r requirements.txt
```

Step 2: (Optional) Install OCR dependencies for scanned PDFs
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases
- Add both to system PATH, or place poppler folder in project directory

Step 3: Start the server
```
python main.py
```
Or use: `start.bat`

Step 4: Open browser
Go to: http://localhost:8000


## How to Use

1. Click "Choose PDF File" and select a PDF
2. Enter a table name (like "invoices" or "sales_data")
3. Click "Upload & Extract"
4. View the extracted data in the dropdown
5. Double-click any row to edit it
6. Use the buttons to add rows, export to Excel, or delete


## Common Issues

Problem: "Error processing PDF" with image-based PDFs
Solution: Install Tesseract and Poppler

Problem: Module not found errors
Solution: Run "pip install -r requirements.txt" again

Problem: Port 8000 already in use
Solution: Close other applications using that port, or change port in main.py


## Project Files

```
ver-2/
  main.py           - FastAPI application with web interface
  pdf_extractor.py  - PDF extraction logic (text and OCR)
  database.py       - Database operations
  config.py         - Configuration settings
  requirements.txt  - Python dependencies
```


## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/upload?table_name=name` | Upload PDF and extract data |
| GET | `/tables` | List all tables |
| GET | `/data/{table_name}` | Get table data |
| GET | `/schema/{table_name}` | Get table structure |
| GET | `/export/{table_name}` | Download as Excel |
| DELETE | `/table/{table_name}` | Delete table |
| POST | `/table/{table_name}/row` | Add row |
| PUT | `/table/{table_name}/row/{id}` | Update row |
| DELETE | `/table/{table_name}/row/{id}` | Delete row |


## How It Works

1. User uploads a PDF file
2. System tries to extract tables using pdfplumber (for text-based PDFs)
3. If no data found, system attempts OCR extraction using Tesseract
4. Extracted data is converted to JSON format
5. Database table is created or updated based on JSON keys
6. Data is stored in SQLite database
7. User can view, edit, export, or delete data through web interface


## Important Notes

- First row of tables is treated as column headers
- Column names are cleaned (lowercase, underscores replace spaces)
- Column names starting with numbers get 'col_' prefix
- 'id' column is renamed to 'record_id' to avoid database conflicts
- OCR may have errors - use the edit feature to correct them
- Uploaded PDFs are deleted after processing to save space
- System works without OCR dependencies, but only for text-based PDFsTest with sample PDFs:
1. Invoices with tables
2. Balance sheets
3. Financial reports
4. Mixed content (tables + text)

## 📄 License

This is an assessment project for Onestack internship.

---

**Developer**: Saurav Kumar <br/>
**Date**: December 5, 2025  
**Assessment**: Onestack SDE Intern - Question 2

