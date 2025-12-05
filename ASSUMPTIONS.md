# Assumptions

This document lists the assumptions made while building this system.


## PDF Structure

- Tables in PDFs have column headers in the first row
- Empty cells are stored as NULL in database
- If no tables found, system tries to extract key-value pairs from text
- If normal extraction fails, system tries OCR (if available)


## Data Types

- Numbers without decimals are stored as integers
- Numbers with decimals are stored as floats
- Everything else is stored as text
- Empty values are stored as NULL


## Column Names

- Special characters are removed
- Spaces become underscores
- Everything is lowercase
- Names starting with numbers get "col_" prefix (e.g., "3_months" becomes "col_3_months")
- "id" is renamed to "record_id" (to avoid conflict with database primary key)


## Database

- SQLite is used (creates pdf_data.db file automatically)
- Each table has an auto-incrementing "id" as primary key
- New columns are added automatically when new data fields appear
- Existing columns are never deleted


## File Handling

- Only PDF files are accepted
- Maximum file size is 10MB
- Uploaded files are deleted after processing


## OCR (Optical Character Recognition)

- OCR is only attempted if normal extraction returns no data
- Requires Tesseract OCR and Poppler to be installed
- System works without OCR, but only for text-based PDFs
- OCR results may have errors and should be reviewed manually
- OCR-extracted records are tagged with extraction_method = "tesseract_ocr"


## Web Interface

- Works on modern browsers (Chrome, Firefox, Edge, Safari)
- Single page application (no routing)
- Double-click any row to edit it
- Tables reload automatically after uploads


## Limitations

- Merged cells in tables may not extract correctly
- Handwritten text is not supported
- Non-English languages need additional Tesseract language packs
- Large PDFs (100+ pages) may be slow to process
- No user authentication (single user system)