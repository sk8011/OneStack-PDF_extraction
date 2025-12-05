import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database settings
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'pdf_data.db')}"

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf'}

# Max file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024
