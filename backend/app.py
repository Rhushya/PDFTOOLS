# Backend Flask Application - Main Application File
# File: backend/app.py
# Uses temporary cache storage that auto-cleans on shutdown

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import atexit
import signal
import sys
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
import zipfile
import shutil

# Load environment variables
load_dotenv()

# Initialize Flask app with static folder support
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ============================================================================
# TEMPORARY CACHE STORAGE SYSTEM
# All files are stored in temp directory and cleaned up on server shutdown
# ============================================================================

# Create a unique temp directory for this session
SESSION_TEMP_DIR = tempfile.mkdtemp(prefix='pdfmaster_')
UPLOAD_FOLDER = os.path.join(SESSION_TEMP_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(SESSION_TEMP_DIR, 'outputs')
TEMP_FOLDER = os.path.join(SESSION_TEMP_DIR, 'temp')

# Create subdirectories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

print(f"\n{'='*60}")
print(f"  PDFMaster Backend Server")
print(f"{'='*60}")
print(f"  Session temp directory: {SESSION_TEMP_DIR}")
print(f"  All files will be automatically cleaned on shutdown")
print(f"{'='*60}\n")

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 100)) * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,docx,doc,pptx,ppt,xlsx,xls,html').split(','))

def cleanup_temp_directory():
    """Clean up the temporary directory on server shutdown"""
    try:
        if os.path.exists(SESSION_TEMP_DIR):
            shutil.rmtree(SESSION_TEMP_DIR)
            print(f"\n✅ Cleaned up temporary files: {SESSION_TEMP_DIR}")
    except Exception as e:
        print(f"\n⚠️ Error cleaning up temp directory: {e}")

# Register cleanup function to run on exit
atexit.register(cleanup_temp_directory)

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n\n🛑 Server shutting down...")
    cleanup_temp_directory()
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Import utility modules
try:
    from utils.pdf_handler import PDFHandler
    from utils.converter import Converter, ImageHandler, DocumentHandler, OCRHandler
except ImportError as e:
    print(f"Warning: Some utility modules not yet created: {e}")
    
    class PDFHandler:
        pass
    class ImageHandler:
        pass
    class DocumentHandler:
        pass
    class Converter:
        pass
    class OCRHandler:
        pass

# Initialize handlers
pdf_handler = PDFHandler(output_dir=TEMP_FOLDER)
image_handler = ImageHandler()
doc_handler = DocumentHandler()
converter = Converter()
ocr_handler = OCRHandler()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_file_id():
    return str(uuid.uuid4())

def get_file_info(filepath):
    if os.path.exists(filepath):
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'name': os.path.basename(filepath)
        }
    return None

def success_response(message, data=None, status=200):
    return jsonify({
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'data': data or {}
    }), status

def error_response(message, error=None, status=400):
    return jsonify({
        'success': False,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'error': str(error) if error else None
    }), status

def save_uploaded_file(file):
    """Save uploaded file and return file_id and path"""
    if file and allowed_file(file.filename):
        file_id = generate_file_id()
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{file_id}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        return file_id, filepath, filename
    return None, None, None

def save_uploaded_files(files):
    """Save multiple uploaded files"""
    saved_files = []
    for file in files:
        file_id, filepath, original_name = save_uploaded_file(file)
        if file_id:
            saved_files.append({
                'file_id': file_id,
                'filepath': filepath,
                'original_name': original_name
            })
    return saved_files

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return success_response('Server is healthy', {
        'timestamp': datetime.now().isoformat(),
        'status': 'operational',
        'cache_mode': 'temporary',
        'session_dir': SESSION_TEMP_DIR
    })

@app.route('/api/status', methods=['GET'])
def status():
    # Count files in cache
    upload_count = len(os.listdir(UPLOAD_FOLDER)) if os.path.exists(UPLOAD_FOLDER) else 0
    output_count = len(os.listdir(OUTPUT_FOLDER)) if os.path.exists(OUTPUT_FOLDER) else 0
    
    return success_response('API is operational', {
        'version': '1.0.0',
        'cache_mode': 'temporary',
        'cached_uploads': upload_count,
        'cached_outputs': output_count,
        'timestamp': datetime.now().isoformat()
    })

def get_all_endpoints():
    """Get list of all available endpoints"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule)
            })
    return endpoints

# ============================================================================
# FILE UPLOAD ENDPOINT
# ============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return error_response('No files provided')
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return error_response('No files selected')
        
        saved_files = save_uploaded_files(files)
        
        if not saved_files:
            return error_response('No valid files uploaded')
        
        return success_response('Files uploaded successfully', {
            'files': saved_files,
            'count': len(saved_files)
        })
    except Exception as e:
        return error_response('Error uploading files', error=e, status=500)

# ============================================================================
# PDF OPERATIONS
# ============================================================================

@app.route('/api/pdf/merge', methods=['POST'])
def merge_pdfs():
    try:
        if 'files' not in request.files:
            return error_response('No PDF files provided')
        
        files = request.files.getlist('files')
        if len(files) < 2:
            return error_response('At least 2 PDF files required for merging')
        
        # Save uploaded files
        saved_files = save_uploaded_files(files)
        input_paths = [f['filepath'] for f in saved_files]
        
        # Generate output
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_merged.pdf")
        
        # Merge PDFs
        result = pdf_handler.merge_pdfs(input_paths, output_path)
        
        if result['success']:
            return success_response('PDFs merged successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_merged.pdf",
                'download_url': f"/download/{output_id}_merged.pdf"
            })
        else:
            return error_response('Failed to merge PDFs', error=result.get('error'))
    except Exception as e:
        return error_response('Error merging PDFs', error=e, status=500)

@app.route('/api/pdf/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        pages = request.form.get('pages', '1')  # e.g., "1-3" or "1,3,5"
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], output_id)
        os.makedirs(output_dir, exist_ok=True)
        
        result = pdf_handler.split_pdf(filepath, output_dir, pages)
        
        if result['success']:
            return success_response('PDF split successfully', {
                'file_id': output_id,
                'pages': result.get('pages', []),
                'download_url': f"/download/{output_id}/page_1.pdf"
            })
        else:
            return error_response('Failed to split PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error splitting PDF', error=e, status=500)

@app.route('/api/pdf/rotate', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        angle = int(request.form.get('angle', 90))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_rotated.pdf")
        
        result = pdf_handler.rotate_pdf(filepath, output_path, angle)
        
        if result['success']:
            return success_response('PDF rotated successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_rotated.pdf",
                'download_url': f"/download/{output_id}_rotated.pdf"
            })
        else:
            return error_response('Failed to rotate PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error rotating PDF', error=e, status=500)

@app.route('/api/pdf/compress', methods=['POST'])
def compress_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        quality = request.form.get('quality', 'medium')  # low, medium, high
        target_reduction = request.form.get('target_reduction')  # Optional: 10-90%
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_compressed.pdf")
        
        result = pdf_handler.compress_pdf(filepath, output_path, quality, target_reduction)
        
        if result['success']:
            return success_response('PDF compressed successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_compressed.pdf",
                'original_size': result.get('original_size'),
                'compressed_size': result.get('compressed_size'),
                'reduction': result.get('reduction'),
                'download_url': f"/download/{output_id}_compressed.pdf"
            })
        else:
            return error_response('Failed to compress PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error compressing PDF', error=e, status=500)

@app.route('/api/pdf/watermark', methods=['POST'])
def add_watermark():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        text = request.form.get('text', 'WATERMARK')
        opacity = float(request.form.get('opacity', 0.3))
        angle = int(request.form.get('angle', 45))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_watermarked.pdf")
        
        result = pdf_handler.add_watermark(filepath, output_path, text, opacity, angle)
        
        if result['success']:
            return success_response('Watermark added successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_watermarked.pdf",
                'download_url': f"/download/{output_id}_watermarked.pdf"
            })
        else:
            return error_response('Failed to add watermark', error=result.get('error'))
    except Exception as e:
        return error_response('Error adding watermark', error=e, status=500)

@app.route('/api/pdf/page-numbers', methods=['POST'])
def add_page_numbers():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        position = request.form.get('position', 'bottom-center')
        start_number = int(request.form.get('start', 1))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_numbered.pdf")
        
        result = pdf_handler.add_page_numbers(filepath, output_path, position, start_number)
        
        if result['success']:
            return success_response('Page numbers added successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_numbered.pdf",
                'download_url': f"/download/{output_id}_numbered.pdf"
            })
        else:
            return error_response('Failed to add page numbers', error=result.get('error'))
    except Exception as e:
        return error_response('Error adding page numbers', error=e, status=500)

@app.route('/api/pdf/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        output_format = request.form.get('format', 'txt')  # txt or docx
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        ext = 'docx' if output_format == 'docx' else 'txt'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_text.{ext}")
        
        result = pdf_handler.extract_text(filepath, output_path, output_format)
        
        if result['success']:
            return success_response('Text extracted successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_text.{ext}",
                'text_preview': result.get('text_preview', ''),
                'char_count': result.get('char_count', 0),
                'word_count': result.get('word_count', 0),
                'download_url': f"/download/{output_id}_text.{ext}"
            })
        else:
            return error_response('Failed to extract text', error=result.get('error'))
    except Exception as e:
        return error_response('Error extracting text', error=e, status=500)

@app.route('/api/pdf/extract-images', methods=['POST'])
def extract_images():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_images")
        os.makedirs(output_dir, exist_ok=True)
        
        result = pdf_handler.extract_images(filepath, output_dir)
        
        if result['success']:
            # Create zip of images
            zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{output_id}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img in result.get('images', []):
                    zipf.write(img, os.path.basename(img))
            
            return success_response('Images extracted successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_images.zip",
                'image_count': result.get('image_count', 0),
                'download_url': f"/download-zip/{output_id}"
            })
        else:
            return error_response('Failed to extract images', error=result.get('error'))
    except Exception as e:
        return error_response('Error extracting images', error=e, status=500)

@app.route('/api/pdf/extract-tables', methods=['POST'])
def extract_tables():
    """Extract tables from PDF"""
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        output_format = request.form.get('format', 'txt')  # txt or markdown
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_tables")
        os.makedirs(output_dir, exist_ok=True)
        
        result = pdf_handler.extract_tables(filepath, output_dir, output_format)
        
        if result['success']:
            ext = 'md' if output_format == 'markdown' else 'txt'
            return success_response('Tables extracted successfully', {
                'file_id': output_id,
                'filename': f"tables.{ext}",
                'tables_count': result.get('tables_count', 0),
                'download_url': f"/download/{output_id}_tables/tables.{ext}"
            })
        else:
            return error_response('Failed to extract tables', error=result.get('error'))
    except Exception as e:
        return error_response('Error extracting tables', error=e, status=500)

# ============================================================================
# SECURITY OPERATIONS
# ============================================================================

@app.route('/api/security/protect', methods=['POST'])
def protect_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        password = request.form.get('password', '')
        
        if not password:
            return error_response('Password is required')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_protected.pdf")
        
        result = pdf_handler.protect_pdf(filepath, output_path, password)
        
        if result['success']:
            return success_response('PDF protected successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_protected.pdf",
                'download_url': f"/download/{output_id}_protected.pdf"
            })
        else:
            return error_response('Failed to protect PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error protecting PDF', error=e, status=500)

@app.route('/api/security/unlock', methods=['POST'])
def unlock_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        password = request.form.get('password', '')
        
        if not password:
            return error_response('Password is required')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_unlocked.pdf")
        
        result = pdf_handler.unlock_pdf(filepath, output_path, password)
        
        if result['success']:
            return success_response('PDF unlocked successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_unlocked.pdf",
                'download_url': f"/download/{output_id}_unlocked.pdf"
            })
        else:
            return error_response('Failed to unlock PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error unlocking PDF', error=e, status=500)

# ============================================================================
# CONVERSION OPERATIONS
# ============================================================================

@app.route('/api/convert/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        dpi = int(request.form.get('dpi', 150))
        pages = request.form.get('pages', '')  # e.g., "1", "1-3", "1,3,5", or empty for all
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_jpg")
        os.makedirs(output_dir, exist_ok=True)
        
        # Use the enhanced pdf_to_images method
        result = pdf_handler.pdf_to_images(filepath, output_dir, format='jpeg', dpi=dpi, pages=pages if pages else None)
        
        if result['success']:
            images = result.get('images', [])
            
            # If only one image, return it directly; otherwise zip
            if len(images) == 1:
                single_image = images[0]
                import shutil
                final_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_page.jpg")
                shutil.copy(single_image, final_path)
                return success_response('PDF converted to JPG successfully', {
                    'file_id': output_id,
                    'filename': f"{output_id}_page.jpg",
                    'page_count': 1,
                    'total_pages': result.get('total_pages', 1),
                    'download_url': f"/download/{output_id}_page.jpg"
                })
            else:
                # Create zip of images
                zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{output_id}_jpg.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for img in images:
                        zipf.write(img, os.path.basename(img))
                
                return success_response('PDF converted to JPG successfully', {
                    'file_id': output_id,
                    'filename': f"{output_id}_jpg.zip",
                    'page_count': result.get('page_count', 0),
                    'total_pages': result.get('total_pages', 0),
                    'download_url': f"/download-zip/{output_id}_jpg"
                })
        else:
            return error_response('Failed to convert PDF to JPG', error=result.get('error'))
    except Exception as e:
        return error_response('Error converting PDF to JPG', error=e, status=500)

@app.route('/api/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    """Convert PDF to Word document (.docx)"""
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        base_name = os.path.splitext(original_name)[0]
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_{base_name}.docx")
        
        result = pdf_handler.pdf_to_word(filepath, output_path)
        
        if result['success']:
            return success_response('PDF converted to Word successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_{base_name}.docx",
                'page_count': result.get('page_count', 0),
                'download_url': f"/download/{output_id}_{base_name}.docx"
            })
        else:
            return error_response('Failed to convert PDF to Word', error=result.get('error'))
    except Exception as e:
        return error_response('Error converting PDF to Word', error=e, status=500)

@app.route('/api/convert/pdf-to-png', methods=['POST'])
def pdf_to_png():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        dpi = int(request.form.get('dpi', 150))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file type')
        
        output_id = generate_file_id()
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_png")
        os.makedirs(output_dir, exist_ok=True)
        
        result = converter.pdf_to_png(filepath, output_dir, dpi)
        
        if result['success']:
            # Create zip of images
            zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{output_id}_png.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img in result.get('images', []):
                    zipf.write(img, os.path.basename(img))
            
            return success_response('PDF converted to PNG successfully', {
                'file_id': output_id,
                'page_count': result.get('page_count', 0),
                'download_url': f"/download-zip/{output_id}_png"
            })
        else:
            return error_response('Failed to convert PDF to PNG', error=result.get('error'))
    except Exception as e:
        return error_response('Error converting PDF to PNG', error=e, status=500)

@app.route('/api/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    try:
        if 'files' not in request.files:
            return error_response('No image files provided')
        
        files = request.files.getlist('files')
        if not files:
            return error_response('No files selected')
        
        saved_files = save_uploaded_files(files)
        input_paths = [f['filepath'] for f in saved_files]
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_from_images.pdf")
        
        result = converter.images_to_pdf(input_paths, output_path)
        
        if result['success']:
            return success_response('Images converted to PDF successfully', {
                'file_id': output_id,
                'filename': f"{output_id}_from_images.pdf",
                'download_url': f"/download/{output_id}_from_images.pdf"
            })
        else:
            return error_response('Failed to convert images to PDF', error=result.get('error'))
    except Exception as e:
        return error_response('Error converting images to PDF', error=e, status=500)

# ============================================================================
# DOWNLOAD ENDPOINTS
# ============================================================================

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        # Check in outputs folder first
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        
        # Check if it's a directory path
        parts = filename.split('/')
        if len(parts) > 1:
            dir_path = os.path.join(app.config['OUTPUT_FOLDER'], parts[0])
            file_path = os.path.join(dir_path, parts[1])
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
        
        return error_response('File not found', status=404)
    except Exception as e:
        return error_response('Error downloading file', error=e, status=500)

@app.route('/download-zip/<file_id>', methods=['GET'])
def download_zip(file_id):
    try:
        zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{file_id}.zip")
        if os.path.exists(zip_path):
            return send_file(zip_path, as_attachment=True, download_name=f"{file_id}.zip")
        return error_response('File not found', status=404)
    except Exception as e:
        return error_response('Error downloading file', error=e, status=500)

# ============================================================================
# STATIC FILE SERVING (for production)
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting PDFMaster API on http://localhost:{port}")
    print(f"📁 Cache directory: {SESSION_TEMP_DIR}")
    print(f"⚠️  Files will be deleted when server stops\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_temp_directory()
