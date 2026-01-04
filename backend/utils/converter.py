# Document & Format Converter Module
# File: backend/utils/converter.py

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import fitz  # PyMuPDF
import os
from io import BytesIO

# Optional imports - handle gracefully if not installed
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

try:
    from openpyxl import load_workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class Converter:
    """
    Comprehensive document format converter
    Returns dict with 'success' key for all operations
    """
    
    def __init__(self):
        self.supported_conversions = {
            'jpg_to_pdf': 'Convert JPG images to PDF',
            'png_to_pdf': 'Convert PNG images to PDF',
            'pdf_to_jpg': 'Convert PDF pages to JPG',
            'pdf_to_png': 'Convert PDF pages to PNG',
        }
    
    def images_to_pdf(self, image_paths, output_path):
        """Convert images to PDF"""
        try:
            images = []
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img)
            
            if images:
                first_image = images[0]
                
                if len(images) > 1:
                    first_image.save(
                        output_path,
                        save_all=True,
                        append_images=images[1:],
                        format='PDF'
                    )
                else:
                    first_image.save(output_path, format='PDF')
                
                for img in images:
                    img.close()
                
                return {'success': True, 'output_path': output_path, 'page_count': len(images)}
            return {'success': False, 'error': 'No valid images found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pdf_to_jpg(self, input_path, output_dir, dpi=150, pages=None):
        """Convert PDF pages to JPG images"""
        output_paths = []
        
        # Try pdf2image first if available
        if PDF2IMAGE_AVAILABLE:
            try:
                images = convert_from_path(input_path, dpi=dpi)
                for i, image in enumerate(images):
                    if pages is None or (i + 1) in pages:
                        output_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
                        image.save(output_path, 'JPEG', quality=95)
                        output_paths.append(output_path)
                return {'success': True, 'images': output_paths, 'page_count': len(output_paths)}
            except Exception as e:
                # Fall through to PyMuPDF
                pass
        
        # Use PyMuPDF as fallback
        try:
            doc = fitz.open(input_path)
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            
            for i, page in enumerate(doc):
                if pages is None or (i + 1) in pages:
                    pix = page.get_pixmap(matrix=matrix)
                    output_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
                    pix.save(output_path)
                    output_paths.append(output_path)
            
            doc.close()
            return {'success': True, 'images': output_paths, 'page_count': len(output_paths)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pdf_to_png(self, input_path, output_dir, dpi=150, pages=None):
        """Convert PDF pages to PNG images"""
        output_paths = []
        
        # Try pdf2image first if available
        if PDF2IMAGE_AVAILABLE:
            try:
                images = convert_from_path(input_path, dpi=dpi)
                for i, image in enumerate(images):
                    if pages is None or (i + 1) in pages:
                        output_path = os.path.join(output_dir, f"page_{i + 1}.png")
                        image.save(output_path, 'PNG')
                        output_paths.append(output_path)
                return {'success': True, 'images': output_paths, 'page_count': len(output_paths)}
            except Exception as e:
                # Fall through to PyMuPDF
                pass
        
        # Use PyMuPDF as fallback
        try:
            doc = fitz.open(input_path)
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            
            for i, page in enumerate(doc):
                if pages is None or (i + 1) in pages:
                    pix = page.get_pixmap(matrix=matrix)
                    output_path = os.path.join(output_dir, f"page_{i + 1}.png")
                    pix.save(output_path)
                    output_paths.append(output_path)
            
            doc.close()
            return {'success': True, 'images': output_paths, 'page_count': len(output_paths)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ImageHandler:
    """Handles image manipulation operations"""
    
    def __init__(self):
        pass
    
    def resize_image(self, input_path, output_path, width=None, height=None):
        """Resize an image"""
        try:
            img = Image.open(input_path)
            
            if width and height:
                img = img.resize((width, height), Image.LANCZOS)
            elif width:
                ratio = width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((width, new_height), Image.LANCZOS)
            elif height:
                ratio = height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
            
            img.save(output_path)
            img.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DocumentHandler:
    """Handles document operations"""
    
    def __init__(self):
        pass


class OCRHandler:
    """Handles OCR operations"""
    
    def __init__(self):
        pass
    
    def extract_text_ocr(self, input_path):
        """Extract text using OCR"""
        try:
            import pytesseract
            img = Image.open(input_path)
            text = pytesseract.image_to_string(img)
            img.close()
            return {'success': True, 'text': text}
        except ImportError:
            return {'success': False, 'error': 'pytesseract not installed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
