# PDFMaster - Complete PDF Manipulation Solution

A powerful, full-stack PDF manipulation platform featuring a modern React frontend and Python Flask backend. Process PDFs locally with no file size limits, no cloud uploads, and complete privacy.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Quick Start](#quick-start)
7. [API Reference](#api-reference)
8. [Frontend Architecture](#frontend-architecture)
9. [Backend Architecture](#backend-architecture)
10. [Desktop Application](#desktop-application)
11. [Configuration](#configuration)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)

---

## Overview

PDFMaster is an all-in-one PDF toolkit that runs entirely on your local machine. Unlike cloud-based alternatives, your files never leave your computer, ensuring complete privacy and security. The application features a sleek, modern UI with smooth animations and a comprehensive set of PDF manipulation tools.

### Key Benefits

- **Complete Privacy**: All processing happens locally on your machine
- **No File Size Limits**: Process large PDFs without restrictions
- **No Internet Required**: Works offline after installation
- **Free and Open Source**: MIT licensed for personal and commercial use
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Desktop App Available**: Standalone Electron application

---

## Features

### PDF Organization

| Feature | Description |
|---------|-------------|
| Merge PDFs | Combine multiple PDF files into a single document |
| Split PDF | Extract specific pages or split into multiple files |
| Rotate Pages | Rotate PDF pages by 90, 180, or 270 degrees |
| Rearrange Pages | Reorder pages within a PDF document |
| Remove Pages | Delete specific pages from a PDF |

### Document Enhancement

| Feature | Description |
|---------|-------------|
| Add Watermark | Apply custom text watermarks with adjustable opacity and angle |
| Add Page Numbers | Insert page numbers at various positions (top/bottom, left/center/right) |
| Compress PDF | Reduce file size with configurable quality settings (low/medium/high) |

### Content Extraction

| Feature | Description |
|---------|-------------|
| Extract Text | Export text content to TXT or DOCX format |
| Extract Images | Pull all embedded images as JPG or PNG files |
| Extract Tables | Export tables as text or markdown format |

### Format Conversion

| Feature | Description |
|---------|-------------|
| Image to PDF | Convert JPG, PNG, GIF, BMP images to PDF |
| PDF to JPG | Convert PDF pages to high-quality JPG images |
| PDF to PNG | Convert PDF pages to PNG images with transparency |
| PDF to Word | Convert PDF documents to DOCX format |

### Security Operations

| Feature | Description |
|---------|-------------|
| Password Protect | Encrypt PDFs with AES-256 bit encryption |
| Unlock PDF | Remove password protection from encrypted PDFs |

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Core runtime environment |
| Flask | 3.0.0 | REST API web framework |
| Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| PyMuPDF (fitz) | 1.23.7 | PDF rendering and manipulation |
| PyPDF2 | 3.0.1 | PDF merging and splitting |
| pypdf | 5.0.0+ | PDF compression |
| pdf2docx | 0.5.6+ | PDF to Word conversion |
| ReportLab | 4.0.7 | PDF generation |
| Pillow | 10.1.0 | Image processing |
| python-docx | 1.1.0 | Word document creation |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI component library |
| TypeScript | 5.9.3 | Type-safe development |
| Vite | 7.2.5 | Build tool and dev server |
| Framer Motion | 12.23.26 | Animations and transitions |
| React Dropzone | 14.3.8 | Drag-and-drop file uploads |
| React Hot Toast | 2.6.0 | Toast notifications |
| Lucide React | 0.562.0 | Icon library |
| Axios | 1.13.2 | HTTP client |

### Desktop Application

| Technology | Version | Purpose |
|------------|---------|---------|
| Electron | 28.1.0 | Cross-platform desktop wrapper |
| electron-builder | 24.9.1 | Application packaging |

---

## Project Structure

```
pdf/
├── README.md                 # Project documentation
├── start.bat                 # One-click launcher script
├── test_api.py               # API endpoint tests
├── test_operations.py        # PDF operations tests
│
├── backend/
│   ├── app.py                # Flask REST API (main application)
│   ├── requirements.txt      # Python dependencies
│   ├── README.md             # Backend documentation
│   └── utils/
│       ├── __init__.py       # Package initializer
│       ├── pdf_handler.py    # PDF manipulation operations
│       └── converter.py      # Format conversion operations
│
├── frontend/
│   ├── package.json          # Node.js dependencies and scripts
│   ├── vite.config.ts        # Vite configuration
│   ├── tsconfig.json         # TypeScript configuration
│   ├── index.html            # HTML entry point
│   ├── README.md             # Frontend documentation
│   ├── electron/
│   │   └── main.js           # Electron main process
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   ├── App.css           # Component styles
│   │   ├── index.css         # Global styles
│   │   └── main.tsx          # React entry point
│   └── dist/                 # Production build output
│
├── logs/                     # Application logs
│   ├── backend.log
│   └── frontend.log
│
├── uploads/                  # Temporary upload directory
├── outputs/                  # Processed file output
└── temp/                     # Temporary processing files
```

---

## Installation

### Prerequisites

- **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/)
- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- **Conda** (optional but recommended): Download from [conda.io](https://docs.conda.io/en/latest/miniconda.html)

### Backend Setup

Using Conda (Recommended):

```bash
# Create and activate conda environment
conda create -n pdfmaster python=3.12 -y
conda activate pdfmaster

# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

Using pip directly:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

---

## Quick Start

### Option 1: One-Click Start (Windows)

Double-click `start.bat` in the root directory. This script will:
1. Launch the Flask backend server on http://localhost:5000
2. Wait for the backend to initialize
3. Launch the Vite frontend server on http://localhost:5173

### Option 2: Manual Start

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
conda activate pdfmaster  # or activate your virtual environment
python app.py
```
Backend starts at: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend starts at: http://localhost:5173

### Option 3: Run Electron Desktop App

```bash
cd frontend
npm run electron:dev
```

---

## API Reference

All API endpoints are prefixed with `/api` and return JSON responses in the following format:

```json
{
  "success": true,
  "message": "Operation description",
  "timestamp": "2024-01-04T12:00:00.000000",
  "data": {
    "file_id": "unique-uuid",
    "filename": "output.pdf",
    "download_url": "/download/output.pdf"
  }
}
```

### Health and Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/status` | GET | API status and cache information |

### File Upload

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload files for processing |

Request: `multipart/form-data` with `files` field

### PDF Operations

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/pdf/merge` | POST | `files` (multiple) | Merge multiple PDFs |
| `/api/pdf/split` | POST | `file`, `pages` (e.g., "1-3" or "1,3,5") | Split PDF by pages |
| `/api/pdf/rotate` | POST | `file`, `angle` (90, 180, 270) | Rotate all pages |
| `/api/pdf/compress` | POST | `file`, `quality` (low/medium/high), `target_reduction` (10-90) | Compress PDF |
| `/api/pdf/watermark` | POST | `file`, `text`, `opacity` (0.1-1.0), `angle` | Add text watermark |
| `/api/pdf/page-numbers` | POST | `file`, `position` (top/bottom-left/center/right), `start` | Add page numbers |
| `/api/pdf/extract-text` | POST | `file`, `format` (txt/docx) | Extract text content |
| `/api/pdf/extract-images` | POST | `file` | Extract all images |
| `/api/pdf/extract-tables` | POST | `file`, `format` (txt/markdown) | Extract tables |

### Conversion Operations

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/convert/image-to-pdf` | POST | `files` (multiple images) | Convert images to PDF |
| `/api/convert/pdf-to-jpg` | POST | `file`, `dpi` (default: 150), `pages` | Convert PDF to JPG |
| `/api/convert/pdf-to-png` | POST | `file`, `dpi` (default: 150) | Convert PDF to PNG |
| `/api/convert/pdf-to-word` | POST | `file` | Convert PDF to DOCX |

### Security Operations

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/security/protect` | POST | `file`, `password` | Password protect PDF |
| `/api/security/unlock` | POST | `file`, `password` | Remove password protection |

### Download Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/download/<filename>` | GET | Download processed file |
| `/download-zip/<file_id>` | GET | Download ZIP archive |

---

## Frontend Architecture

### Component Structure

The frontend is built as a single-page application with the following key components:

- **App.tsx**: Main application component containing:
  - Hero section with animated background
  - Feature cards with hover effects
  - Tool grid with category filtering
  - Operation modal for file processing
  - Download modal with custom filename support

### State Management

The application uses React hooks for state management:

- `files`: Array of uploaded files
- `selectedOperation`: Currently selected PDF operation
- `selectedCategory`: Active filter category
- `isProcessing`: Processing state flag
- `progress`: Upload/processing progress
- `downloadUrl`: Resulting file download URL

### Styling Features

- Glass-morphism design with backdrop blur
- Gradient animations and color transitions
- Framer Motion for smooth animations
- Responsive layout for all screen sizes
- Dark theme with vibrant accent colors

### Category System

Operations are organized into categories:
- **All Tools**: Complete list of operations
- **Organize**: Merge, Split, Rotate
- **Convert**: Image to PDF, PDF to JPG/PNG/Word
- **Enhance**: Watermark, Page Numbers
- **Extract**: Text, Images, Tables
- **Security**: Protect, Unlock

---

## Backend Architecture

### Temporary Cache System

The backend uses a session-based temporary storage system:

- Creates a unique temp directory for each server session
- All uploads and outputs are stored in the session directory
- Automatic cleanup on server shutdown (graceful or forced)
- Signal handlers for SIGINT and SIGTERM

### Request Flow

1. File uploaded via multipart/form-data
2. File saved to session temp directory with UUID
3. Operation performed using appropriate handler
4. Output saved to outputs directory
5. Download URL returned to frontend
6. Files auto-cleaned on session end

### Handler Classes

**PDFHandler** (`pdf_handler.py`):
- Core PDF operations using PyMuPDF and PyPDF2
- Validates inputs and handles encrypted PDFs
- Returns standardized response dictionaries

**Converter** (`converter.py`):
- Format conversion operations
- Uses pdf2image with PyMuPDF fallback
- Handles batch image processing

**ImageHandler** (`converter.py`):
- Image manipulation operations
- Resize, format conversion

**OCRHandler** (`converter.py`):
- Optional OCR text extraction
- Uses pytesseract when available

### Error Handling

All operations return a consistent response format:

```python
{
    'success': True/False,
    'error': 'Error message if failed',
    'output_path': '/path/to/output',
    # Additional operation-specific data
}
```

---

## Desktop Application

### Building from Source

**Windows:**
```bash
cd frontend
npm run build
npm run electron:build:win
```

**macOS:**
```bash
cd frontend
npm run build
npm run electron:build:mac
```

**Linux:**
```bash
cd frontend
npm run build
npm run electron:build:linux
```

### Build Output

Built applications are saved to `frontend/release/`:

- **Windows**: `.exe` installer and portable executable
- **macOS**: `.dmg` disk image and `.zip` archive
- **Linux**: `.AppImage` and `.deb` package

### Electron Configuration

The Electron app bundles the Flask backend and serves the React frontend. Key settings:

- App ID: `com.pdfmaster.app`
- Icons: Located in `frontend/public/`
- Backend included in extraResources

---

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False

# Server Settings
HOST=0.0.0.0
PORT=5000

# Security
SECRET_KEY=your-secure-secret-key

# File Handling
MAX_FILE_SIZE=100
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,docx,doc,pptx,ppt,xlsx,xls,html

# Directories (auto-created in temp)
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
```

### Frontend Environment

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:5000/api
```

---

## Troubleshooting

### Common Issues

**Backend fails to start:**
- Ensure Python 3.12+ is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is available

**Frontend fails to start:**
- Ensure Node.js 18+ is installed
- Run `npm install` to ensure all packages are installed
- Check if port 5173 is available

**PDF operations fail:**
- Ensure the PDF is not corrupted
- For encrypted PDFs, provide the correct password
- Check backend logs for detailed error messages

**File upload fails:**
- Verify file type is supported
- Check file size against MAX_FILE_SIZE setting
- Ensure upload directory is writable

**Desktop app issues:**
- Run `npm run electron:dev` for debugging
- Check Electron main process logs
- Verify backend is bundled in extraResources

### Log Files

Application logs are stored in the `logs/` directory:
- `backend.log`: Flask server logs
- `frontend.log`: Vite dev server logs

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## License

MIT License

Copyright (c) 2026 PDFMaster

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**PDFMaster** - Transform. Organize. Accelerate.
