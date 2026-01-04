# Backend Flask Application - Main Application File
# File: backend/app.py

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
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

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 100)) * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', 'outputs')
app.config['TEMP_FOLDER'] = os.getenv('TEMP_FOLDER', 'temp')

ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,docx,doc,pptx,ppt,xlsx,xls,html').split(','))

# Create directories if they don't exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

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
pdf_handler = PDFHandler()
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
        'status': 'operational'
    })

@app.route('/api/status', methods=['GET'])
def status():
    return success_response('API is operational', {
        'version': '1.0.0',
        'endpoints': list(get_all_endpoints()),
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
        success = pdf_handler.merge_pdfs(input_paths, output_path)
        
        if success:
            return success_response('PDFs merged successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_merged.pdf'
            })
        else:
            return error_response('Failed to merge PDFs', status=500)
    except Exception as e:
        return error_response('Error merging PDFs', error=e, status=500)

@app.route('/api/pdf/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        pages = request.form.get('pages', '')  # e.g., "1,3,5-7"
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        # Parse pages
        page_list = parse_page_range(pages) if pages else None
        
        # Create output directory for split files
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], file_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Split PDF
        output_files = pdf_handler.split_pdf(filepath, page_list, output_dir)
        
        if output_files:
            return success_response('PDF split successfully', {
                'file_id': file_id,
                'files': output_files,
                'download_url': f'/api/download/split/{file_id}'
            })
        else:
            return error_response('Failed to split PDF', status=500)
    except Exception as e:
        return error_response('Error splitting PDF', error=e, status=500)

@app.route('/api/pdf/rotate', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        angle = int(request.form.get('angle', 90))
        pages = request.form.get('pages', '')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_rotated.pdf")
        
        page_list = parse_page_range(pages) if pages else None
        success = pdf_handler.rotate_pages(filepath, output_path, angle, page_list)
        
        if success:
            return success_response('PDF rotated successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_rotated.pdf'
            })
        else:
            return error_response('Failed to rotate PDF', status=500)
    except Exception as e:
        return error_response('Error rotating PDF', error=e, status=500)

@app.route('/api/pdf/compress', methods=['POST'])
def compress_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        quality = request.form.get('quality', 'medium')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_compressed.pdf")
        
        success = pdf_handler.compress_pdf(filepath, output_path, quality)
        
        if success:
            original_size = os.path.getsize(filepath)
            compressed_size = os.path.getsize(output_path)
            savings = ((original_size - compressed_size) / original_size) * 100
            
            return success_response('PDF compressed successfully', {
                'file_id': output_id,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'savings_percent': round(savings, 2),
                'download_url': f'/api/download/{output_id}_compressed.pdf'
            })
        else:
            return error_response('Failed to compress PDF', status=500)
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
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_watermarked.pdf")
        
        success = pdf_handler.add_watermark(filepath, output_path, text, opacity, angle)
        
        if success:
            return success_response('Watermark added successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_watermarked.pdf'
            })
        else:
            return error_response('Failed to add watermark', status=500)
    except Exception as e:
        return error_response('Error adding watermark', error=e, status=500)

@app.route('/api/pdf/page-numbers', methods=['POST'])
def add_page_numbers():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        format_str = request.form.get('format', '{page}/{total}')
        position = request.form.get('position', 'bottom-right')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_numbered.pdf")
        
        success = pdf_handler.add_page_numbers(filepath, output_path, format_str, position)
        
        if success:
            return success_response('Page numbers added successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_numbered.pdf'
            })
        else:
            return error_response('Failed to add page numbers', status=500)
    except Exception as e:
        return error_response('Error adding page numbers', error=e, status=500)

@app.route('/api/pdf/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        use_ocr = request.form.get('use_ocr', 'false').lower() == 'true'
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        text = pdf_handler.extract_text(filepath, use_ocr)
        
        # Save text to file
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_text.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return success_response('Text extracted successfully', {
            'file_id': output_id,
            'text': text[:5000] if len(text) > 5000 else text,  # Truncate for response
            'full_text_length': len(text),
            'download_url': f'/api/download/{output_id}_text.txt'
        })
    except Exception as e:
        return error_response('Error extracting text', error=e, status=500)

@app.route('/api/pdf/extract-images', methods=['POST'])
def extract_images():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        format_type = request.form.get('format', 'jpg')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_images")
        os.makedirs(output_dir, exist_ok=True)
        
        images = pdf_handler.extract_images(filepath, output_dir, format_type)
        
        if images:
            return success_response('Images extracted successfully', {
                'file_id': file_id,
                'images': images,
                'count': len(images),
                'download_url': f'/api/download/images/{file_id}'
            })
        else:
            return error_response('No images found or failed to extract', status=500)
    except Exception as e:
        return error_response('Error extracting images', error=e, status=500)

@app.route('/api/pdf/remove-pages', methods=['POST'])
def remove_pages():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        pages = request.form.get('pages', '')
        
        if not pages:
            return error_response('No pages specified for removal')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_modified.pdf")
        
        page_list = parse_page_range(pages)
        success = pdf_handler.remove_pages(filepath, output_path, page_list)
        
        if success:
            return success_response('Pages removed successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_modified.pdf'
            })
        else:
            return error_response('Failed to remove pages', status=500)
    except Exception as e:
        return error_response('Error removing pages', error=e, status=500)

@app.route('/api/pdf/rearrange', methods=['POST'])
def rearrange_pages():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        order = request.form.get('order', '')  # e.g., "3,1,2,5,4"
        
        if not order:
            return error_response('No page order specified')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_rearranged.pdf")
        
        new_order = [int(p.strip()) for p in order.split(',')]
        success = pdf_handler.rearrange_pages(filepath, output_path, new_order)
        
        if success:
            return success_response('Pages rearranged successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_rearranged.pdf'
            })
        else:
            return error_response('Failed to rearrange pages', status=500)
    except Exception as e:
        return error_response('Error rearranging pages', error=e, status=500)

@app.route('/api/pdf/properties/<file_id>', methods=['GET'])
def get_pdf_properties(file_id):
    try:
        # Find the file
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            for filename in os.listdir(folder):
                if filename.startswith(file_id):
                    filepath = os.path.join(folder, filename)
                    info = pdf_handler.get_pdf_info(filepath)
                    if info:
                        return success_response('PDF properties retrieved', info)
        
        return error_response('File not found', status=404)
    except Exception as e:
        return error_response('Error getting PDF properties', error=e, status=500)

# ============================================================================
# CONVERSION OPERATIONS
# ============================================================================

@app.route('/api/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    try:
        if 'files' not in request.files:
            return error_response('No image files provided')
        
        files = request.files.getlist('files')
        orientation = request.form.get('orientation', 'auto')
        
        saved_files = save_uploaded_files(files)
        input_paths = [f['filepath'] for f in saved_files]
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_converted.pdf")
        
        success = converter.jpg_to_pdf(input_paths, output_path, orientation)
        
        if success:
            return success_response('Images converted to PDF successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_converted.pdf'
            })
        else:
            return error_response('Failed to convert images to PDF', status=500)
    except Exception as e:
        return error_response('Error converting images to PDF', error=e, status=500)

@app.route('/api/convert/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        dpi = int(request.form.get('dpi', 300))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_jpg")
        os.makedirs(output_dir, exist_ok=True)
        
        images = converter.pdf_to_jpg(filepath, output_dir, dpi)
        
        if images:
            return success_response('PDF converted to JPG successfully', {
                'file_id': file_id,
                'images': images,
                'count': len(images),
                'download_url': f'/api/download/images/{file_id}_jpg'
            })
        else:
            return error_response('Failed to convert PDF to JPG', status=500)
    except Exception as e:
        return error_response('Error converting PDF to JPG', error=e, status=500)

@app.route('/api/convert/pdf-to-png', methods=['POST'])
def pdf_to_png():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        dpi = int(request.form.get('dpi', 300))
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"{file_id}_png")
        os.makedirs(output_dir, exist_ok=True)
        
        images = converter.pdf_to_png(filepath, output_dir, dpi)
        
        if images:
            return success_response('PDF converted to PNG successfully', {
                'file_id': file_id,
                'images': images,
                'count': len(images),
                'download_url': f'/api/download/images/{file_id}_png'
            })
        else:
            return error_response('Failed to convert PDF to PNG', status=500)
    except Exception as e:
        return error_response('Error converting PDF to PNG', error=e, status=500)

@app.route('/api/convert/word-to-pdf', methods=['POST'])
def word_to_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No Word file provided')
        
        file = request.files['file']
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_converted.pdf")
        
        success = converter.word_to_pdf(filepath, output_path)
        
        if success:
            return success_response('Word document converted to PDF successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_converted.pdf'
            })
        else:
            return error_response('Failed to convert Word to PDF', status=500)
    except Exception as e:
        return error_response('Error converting Word to PDF', error=e, status=500)

@app.route('/api/convert/html-to-pdf', methods=['POST'])
def html_to_pdf():
    try:
        html_content = request.form.get('html', '')
        page_size = request.form.get('page_size', 'A4')
        
        if 'file' in request.files:
            file = request.files['file']
            file_id, filepath, original_name = save_uploaded_file(file)
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        if not html_content:
            return error_response('No HTML content provided')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_converted.pdf")
        
        success = converter.html_to_pdf(html_content, output_path, page_size)
        
        if success:
            return success_response('HTML converted to PDF successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_converted.pdf'
            })
        else:
            return error_response('Failed to convert HTML to PDF', status=500)
    except Exception as e:
        return error_response('Error converting HTML to PDF', error=e, status=500)

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
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_protected.pdf")
        
        success = pdf_handler.protect_pdf(filepath, output_path, password)
        
        if success:
            return success_response('PDF protected successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_protected.pdf'
            })
        else:
            return error_response('Failed to protect PDF', status=500)
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
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_unlocked.pdf")
        
        success = pdf_handler.unlock_pdf(filepath, output_path, password)
        
        if success:
            return success_response('PDF unlocked successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_unlocked.pdf'
            })
        else:
            return error_response('Failed to unlock PDF. Check password.', status=500)
    except Exception as e:
        return error_response('Error unlocking PDF', error=e, status=500)

@app.route('/api/security/redact', methods=['POST'])
def redact_pdf():
    try:
        if 'file' not in request.files:
            return error_response('No PDF file provided')
        
        file = request.files['file']
        text_to_redact = request.form.get('text', '')
        
        if not text_to_redact:
            return error_response('Text to redact is required')
        
        file_id, filepath, original_name = save_uploaded_file(file)
        if not file_id:
            return error_response('Invalid file')
        
        output_id = generate_file_id()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_id}_redacted.pdf")
        
        success = pdf_handler.redact_text(filepath, output_path, text_to_redact)
        
        if success:
            return success_response('PDF redacted successfully', {
                'file_id': output_id,
                'download_url': f'/api/download/{output_id}_redacted.pdf'
            })
        else:
            return error_response('Failed to redact PDF', status=500)
    except Exception as e:
        return error_response('Error redacting PDF', error=e, status=500)

# ============================================================================
# FILE MANAGEMENT
# ============================================================================

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Check output folder first
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        # Check uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        return error_response('File not found', status=404)
    except Exception as e:
        return error_response('Error downloading file', error=e, status=500)

@app.route('/api/download/images/<folder_id>', methods=['GET'])
def download_images_zip(folder_id):
    try:
        # Find the folder
        for suffix in ['_images', '_jpg', '_png']:
            folder_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{folder_id}{suffix}")
            if os.path.exists(folder_path):
                # Create zip file
                zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{folder_id}.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file in os.listdir(folder_path):
                        zipf.write(os.path.join(folder_path, file), file)
                
                return send_file(zip_path, as_attachment=True, download_name=f"{folder_id}.zip")
        
        return error_response('Folder not found', status=404)
    except Exception as e:
        return error_response('Error creating zip file', error=e, status=500)

@app.route('/api/download/split/<file_id>', methods=['GET'])
def download_split_zip(file_id):
    try:
        folder_path = os.path.join(app.config['OUTPUT_FOLDER'], file_id)
        if os.path.exists(folder_path):
            zip_path = os.path.join(app.config['TEMP_FOLDER'], f"{file_id}_split.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in os.listdir(folder_path):
                    zipf.write(os.path.join(folder_path, file), file)
            
            return send_file(zip_path, as_attachment=True, download_name=f"{file_id}_split.zip")
        
        return error_response('Folder not found', status=404)
    except Exception as e:
        return error_response('Error creating zip file', error=e, status=500)

@app.route('/api/files/recent', methods=['GET'])
def list_recent_files():
    try:
        limit = int(request.args.get('limit', 20))
        files = []
        
        for folder in [app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER']]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'folder': os.path.basename(folder)
                    })
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        files = files[:limit]
        
        return success_response('Recent files retrieved', {
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return error_response('Error listing files', error=e, status=500)

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        deleted = False
        
        for folder in [app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER']]:
            for filename in os.listdir(folder):
                if filename.startswith(file_id):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        deleted = True
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                        deleted = True
        
        if deleted:
            return success_response('File deleted successfully')
        else:
            return error_response('File not found', status=404)
    except Exception as e:
        return error_response('Error deleting file', error=e, status=500)

@app.route('/api/storage/stats', methods=['GET'])
def storage_stats():
    try:
        stats = {}
        total_size = 0
        total_files = 0
        
        for folder_name in ['UPLOAD_FOLDER', 'OUTPUT_FOLDER', 'TEMP_FOLDER']:
            folder = app.config[folder_name]
            folder_size = 0
            folder_files = 0
            
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    folder_size += os.path.getsize(filepath)
                    folder_files += 1
                elif os.path.isdir(filepath):
                    for root, dirs, files in os.walk(filepath):
                        for file in files:
                            folder_size += os.path.getsize(os.path.join(root, file))
                            folder_files += 1
            
            stats[folder_name.lower().replace('_folder', '')] = {
                'size_bytes': folder_size,
                'size_mb': round(folder_size / (1024 * 1024), 2),
                'files': folder_files
            }
            total_size += folder_size
            total_files += folder_files
        
        stats['total'] = {
            'size_bytes': total_size,
            'size_mb': round(total_size / (1024 * 1024), 2),
            'files': total_files
        }
        
        return success_response('Storage stats retrieved', stats)
    except Exception as e:
        return error_response('Error getting storage stats', error=e, status=500)

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    try:
        hours = int(request.form.get('hours', 24))
        cutoff = datetime.now().timestamp() - (hours * 3600)
        
        deleted_count = 0
        deleted_size = 0
        
        for folder in [app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff:
                        size = os.path.getsize(filepath)
                        os.remove(filepath)
                        deleted_count += 1
                        deleted_size += size
                elif os.path.isdir(filepath):
                    if os.path.getmtime(filepath) < cutoff:
                        for root, dirs, files in os.walk(filepath):
                            for file in files:
                                deleted_size += os.path.getsize(os.path.join(root, file))
                                deleted_count += 1
                        shutil.rmtree(filepath)
        
        return success_response('Cleanup completed', {
            'deleted_files': deleted_count,
            'freed_bytes': deleted_size,
            'freed_mb': round(deleted_size / (1024 * 1024), 2)
        })
    except Exception as e:
        return error_response('Error during cleanup', error=e, status=500)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_page_range(page_string):
    """Parse page range string like '1,3,5-7' into list [1,3,5,6,7]"""
    if not page_string:
        return None
    
    pages = []
    parts = page_string.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start.strip()), int(end.strip()) + 1))
        else:
            pages.append(int(part))
    
    return sorted(set(pages))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return error_response('Endpoint not found', status=404)

@app.errorhandler(500)
def internal_error(error):
    return error_response('Internal server error', error=error, status=500)

@app.errorhandler(413)
def request_entity_too_large(error):
    return error_response('File too large. Maximum file size allowed.', status=413)

# ============================================================================
# MAIN EXECUTION
# ============================================================================
# SERVE REACT FRONTEND (Production)
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend in production"""
    static_folder = app.static_folder
    if static_folder and os.path.exists(static_folder):
        if path != "" and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        elif os.path.exists(os.path.join(static_folder, 'index.html')):
            return send_from_directory(static_folder, 'index.html')
    return jsonify({
        'message': 'PDFMaster API Server',
        'version': '1.0.0',
        'docs': '/api/status',
        'health': '/health',
        'note': 'Frontend not built. Run build_production.bat or access the dev server at http://localhost:5173'
    })

# ============================================================================

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    PDFMaster Backend                      ║
    ║                                                           ║
    ║   Server starting on http://{host}:{port}                 ║
    ║   Debug mode: {debug_mode}                                      ║
    ║                                                           ║
    ║   Available endpoints:                                    ║
    ║   - GET  /health                                          ║
    ║   - GET  /api/status                                      ║
    ║   - POST /api/pdf/merge                                   ║
    ║   - POST /api/pdf/split                                   ║
    ║   - POST /api/pdf/rotate                                  ║
    ║   - POST /api/pdf/compress                                ║
    ║   - POST /api/pdf/watermark                               ║
    ║   - POST /api/convert/image-to-pdf                        ║
    ║   - POST /api/convert/pdf-to-jpg                          ║
    ║   - And many more...                                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug_mode)
