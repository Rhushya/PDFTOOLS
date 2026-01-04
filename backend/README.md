# PDFMaster Backend

A comprehensive PDF manipulation REST API built with Flask and Python.

## Quick Start

### Prerequisites
- Conda with Python 3.12 environment named `pdfmaster`

### Running the Server

**Option 1: Using the batch file**
```
Double-click start_server.bat
```

**Option 2: Command line**
```powershell
# Activate conda environment
conda activate pdfmaster

# Navigate to backend folder
cd E:\COMPUTES\PROJECT\pdf\backend

# Run the server
python app.py
```

**Option 3: Direct Python execution**
```powershell
& "C:\Users\rhush\.conda\envs\pdfmaster\python.exe" E:\COMPUTES\PROJECT\pdf\backend\app.py
```

## API Endpoints

### Health & Status
- `GET /health` - Check server health
- `GET /api/status` - Get API status and available endpoints

### PDF Operations
- `POST /api/pdf/merge` - Merge multiple PDFs
- `POST /api/pdf/split` - Split PDF into pages
- `POST /api/pdf/rotate` - Rotate PDF pages
- `POST /api/pdf/compress` - Compress PDF
- `POST /api/pdf/watermark` - Add watermark
- `POST /api/pdf/page-numbers` - Add page numbers
- `POST /api/pdf/extract-text` - Extract text from PDF
- `POST /api/pdf/extract-images` - Extract images from PDF
- `POST /api/pdf/remove-pages` - Remove specific pages
- `POST /api/pdf/rearrange` - Rearrange page order
- `GET /api/pdf/properties/<file_id>` - Get PDF properties

### Conversions
- `POST /api/convert/image-to-pdf` - Convert images to PDF
- `POST /api/convert/pdf-to-jpg` - Convert PDF to JPG images
- `POST /api/convert/pdf-to-png` - Convert PDF to PNG images
- `POST /api/convert/word-to-pdf` - Convert Word to PDF
- `POST /api/convert/html-to-pdf` - Convert HTML to PDF

### Security
- `POST /api/security/protect` - Add password protection
- `POST /api/security/unlock` - Remove password
- `POST /api/security/redact` - Redact sensitive text

### File Management
- `GET /api/download/<filename>` - Download processed file
- `GET /api/files/recent` - List recent files
- `DELETE /api/files/<file_id>` - Delete a file
- `GET /api/storage/stats` - Get storage statistics
- `POST /api/cleanup` - Clean up old files

## Example Usage

### Merge PDFs
```bash
curl -X POST -F "files=@file1.pdf" -F "files=@file2.pdf" http://localhost:5000/api/pdf/merge
```

### Extract Text
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/pdf/extract-text
```

### Add Watermark
```bash
curl -X POST -F "file=@document.pdf" -F "text=CONFIDENTIAL" http://localhost:5000/api/pdf/watermark
```

## Configuration

Environment variables (in `.env`):
- `FLASK_ENV` - development or production
- `DEBUG` - True or False
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `MAX_FILE_SIZE` - Maximum upload size in MB
- `UPLOAD_FOLDER` - Upload directory
- `OUTPUT_FOLDER` - Output directory
- `TEMP_FOLDER` - Temporary files directory

## Installed Packages

Core:
- Flask, Flask-CORS
- PyPDF2, PyMuPDF (fitz)
- Pillow, ReportLab

Office support:
- python-docx, python-pptx, openpyxl

## Notes

- The server runs on http://localhost:5000 by default
- All uploaded files are stored in the `uploads/` folder
- Processed files are stored in the `outputs/` folder
- OCR features require pytesseract (optional)
- PDF to image with pdf2image requires Poppler (optional, uses PyMuPDF fallback)
