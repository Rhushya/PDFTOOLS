# 🎨 PDFMaster - Professional PDF Solution

A beautiful, full-stack PDF manipulation platform with a modern React frontend and Python Flask backend.

![PDFMaster](https://via.placeholder.com/1200x600/0f0f1a/6366f1?text=PDFMaster+-+All+in+One+PDF+Solution)

## ✨ Features

### PDF Operations
- 🔗 **Merge PDFs** - Combine multiple PDFs into one
- ✂️ **Split PDF** - Extract specific pages
- 🔄 **Rotate Pages** - Rotate by 90°, 180°, or 270°
-  **Add Watermark** - Add text watermarks
- 🔢 **Page Numbers** - Add page numbering

### Extraction
- 📝 **Extract Text** - Get text content from PDFs
- 🖼️ **Extract Images** - Pull all images from PDFs

### Conversion
- 📷 **Image to PDF** - Convert JPG, PNG to PDF
- 🖼️ **PDF to JPG** - Convert PDF pages to images

### Security
- 🔒 **Protect PDF** - Add password protection
- 🔓 **Unlock PDF** - Remove passwords

## 🎨 UI Features

- ✨ **Glass-morphism Design** - Modern frosted glass effects
- 🌈 **Gradient Animations** - Smooth color transitions
- 💫 **Framer Motion** - Beautiful animations and transitions
- 🎯 **Drag & Drop** - Easy file uploading
- 📱 **Responsive** - Works on all screen sizes
- 🎪 **Modal Popups** - Blur backdrop with smooth animations
- 📊 **Progress Bars** - Real-time upload/processing feedback
- 🔔 **Toast Notifications** - Non-intrusive alerts

## 🛠️ Tech Stack

### Backend
- Python 3.12 (Conda Environment: `pdfmaster`)
- Flask + Flask-CORS
- PyMuPDF (fitz) - PDF rendering
- PyPDF2 - PDF manipulation
- ReportLab - PDF generation
- Pillow - Image processing
- python-docx, python-pptx, openpyxl - Office documents
- Uvicorn - Production ASGI server

### Frontend
- React + TypeScript
- Vite - Build tool
- Framer Motion - Animations
- React Dropzone - File uploads
- React Hot Toast - Notifications
- Lucide React - Icons
- Axios - HTTP client

## 🚀 Quick Start

### Option 1: One-Click Start (Recommended)
Double-click the `start_pdfmaster.bat` file in the root folder. This will start both backend and frontend automatically.

### Option 2: Manual Start

#### Backend
```bash
cd backend
conda activate pdfmaster
python app.py
```
Server starts at: http://localhost:5000

#### Frontend
```bash
cd frontend
npm run dev
```
Server starts at: http://localhost:5173

## 📁 Project Structure

```
pdf/
├── start_pdfmaster.bat      # Start both servers
├── backend/
│   ├── app.py               # Flask REST API
│   ├── start_server.bat     # Backend launcher
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment config
│   ├── utils/
│   │   ├── pdf_handler.py   # PDF operations
│   │   └── converter.py     # File conversions
│   ├── uploads/             # Uploaded files
│   ├── outputs/             # Processed files
│   └── temp/                # Temporary files
└── frontend/
    ├── start_frontend.bat   # Frontend launcher
    ├── package.json         # Node dependencies
    ├── src/
    │   ├── App.tsx          # Main component
    │   ├── App.css          # Styles
    │   └── index.css        # Global styles
    └── public/
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status` | GET | Server status |
| `/api/pdf/merge` | POST | Merge PDFs |
| `/api/pdf/split` | POST | Split PDF |
| `/api/pdf/rotate` | POST | Rotate pages |
| `/api/pdf/compress` | POST | Compress PDF |
| `/api/pdf/watermark` | POST | Add watermark |
| `/api/pdf/page-numbers` | POST | Add page numbers |
| `/api/pdf/extract-text` | POST | Extract text |
| `/api/pdf/extract-images` | POST | Extract images |
| `/api/convert/image-to-pdf` | POST | Image to PDF |
| `/api/convert/pdf-to-jpg` | POST | PDF to images |
| `/api/security/protect` | POST | Password protect |
| `/api/security/unlock` | POST | Remove password |

## 🎨 Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#6366f1` | Buttons, links |
| Secondary | `#ec4899` | Accents, gradients |
| Accent | `#8b5cf6` | Highlights |
| Success | `#10b981` | Success states |
| Error | `#ef4444` | Error states |
| Background | `#0f0f1a` | Dark background |

## 📦 Installation

### Prerequisites
- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- [Node.js](https://nodejs.org/) (v18+)

### Setup Conda Environment
```bash
conda create -n pdfmaster python=3.12 -y
conda activate pdfmaster
cd backend
pip install -r requirements.txt
```

### Setup Frontend
```bash
cd frontend
npm install
```

## �️ Desktop App

### Download

Download the latest release from the [Releases](../../releases) page:
- **Windows:** `PDFMaster-Setup.exe` (Installer) or `PDFMaster.exe` (Portable)
- **macOS:** `PDFMaster.dmg`
- **Linux:** `PDFMaster.AppImage`

### Build from Source

**Windows:**
```bash
# Run the build script
build-app.bat
```

**All platforms:**
```bash
cd frontend
npm install
npm run build

# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux
```

The built app will be in `frontend/release/`

## �🔧 Configuration

### Backend (.env)
```env
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=5000
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_CONTENT_LENGTH=104857600
```

## 📄 License

MIT License - Feel free to use for personal and commercial projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ using Python & React
