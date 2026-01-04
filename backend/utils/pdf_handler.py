# PDF Handler Utility Module
# File: backend/utils/pdf_handler.py

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import io

class PDFHandler:
    """
    Comprehensive PDF manipulation handler using PyPDF2, PyMuPDF, and ReportLab
    """
    
    def __init__(self):
        self.supported_operations = [
            'merge', 'split', 'rotate', 'crop', 'compress',
            'watermark', 'extract_text', 'extract_images',
            'add_page_numbers', 'remove_pages', 'rearrange',
            'protect', 'unlock', 'redact'
        ]
    
    def merge_pdfs(self, input_files, output_path):
        """
        Merge multiple PDFs into a single document
        
        Args:
            input_files (list): List of PDF file paths
            output_path (str): Output file path
            
        Returns:
            bool: Success status
        """
        try:
            merger = PdfMerger()
            
            for pdf_file in input_files:
                if os.path.exists(pdf_file):
                    merger.append(pdf_file)
            
            merger.write(output_path)
            merger.close()
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False
    
    def split_pdf(self, input_path, pages, output_dir):
        """
        Extract specific pages from PDF
        
        Args:
            input_path (str): Input PDF path
            pages (list): List of page numbers (1-indexed), None for all
            output_dir (str): Output directory
            
        Returns:
            list: List of output file paths
        """
        try:
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            output_files = []
            
            if pages is None:
                pages = list(range(1, total_pages + 1))
            
            for page_num in pages:
                if 1 <= page_num <= total_pages:
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])
                    
                    output_file = os.path.join(output_dir, f"page_{page_num}.pdf")
                    with open(output_file, 'wb') as f:
                        writer.write(f)
                    output_files.append(output_file)
            
            return output_files
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return []
    
    def rotate_pages(self, input_path, output_path, angle, pages=None):
        """
        Rotate PDF pages
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            angle (int): Rotation angle (90, 180, 270)
            pages (list): Pages to rotate (None = all)
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            if pages is None:
                pages = list(range(1, len(doc) + 1))
            
            for page_num in pages:
                if 1 <= page_num <= len(doc):
                    page = doc[page_num - 1]
                    page.set_rotation(page.rotation + angle)
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error rotating PDF: {e}")
            return False
    
    def crop_pdf(self, input_path, output_path, coordinates):
        """
        Crop PDF pages
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            coordinates (list): List of [x0, y0, x1, y1] coordinates
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                rect = fitz.Rect(coordinates)
                page.set_cropbox(rect)
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error cropping PDF: {e}")
            return False
    
    def add_watermark(self, input_path, output_path, text, opacity=0.3, angle=45, color=(0.5, 0.5, 0.5)):
        """
        Add watermark to PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            text (str): Watermark text
            opacity (float): Watermark opacity (0-1)
            angle (int): Rotation angle
            color (tuple): RGB color tuple
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                rect = page.rect
                # Calculate center position
                center = fitz.Point(rect.width / 2, rect.height / 2)
                
                # Create watermark with gray color based on opacity
                gray_value = 1 - (opacity * 0.5)  # Lighter color for visibility
                text_color = (gray_value, gray_value, gray_value)
                
                # Use TextWriter for rotated text
                tw = fitz.TextWriter(page.rect)
                font = fitz.Font("helv")
                fontsize = 60
                
                # Add text centered
                tw.append(center, text, font=font, fontsize=fontsize)
                
                # Create rotation matrix
                mat = fitz.Matrix(1, 0, 0, 1, 0, 0).prerotate(angle)
                
                # Write text with rotation
                tw.write_text(page, morph=(center, mat), color=text_color)
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return False
    
    def add_page_numbers(self, input_path, output_path, format_str="{page}/{total}", position="bottom-right"):
        """
        Add page numbers to PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            format_str (str): Format string for page numbers
            position (str): Position on page
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            for i, page in enumerate(doc):
                rect = page.rect
                page_num = i + 1
                text = format_str.replace("{page}", str(page_num)).replace("{total}", str(total_pages))
                
                # Calculate position
                if position == "bottom-right":
                    x = rect.width - 50
                    y = rect.height - 30
                elif position == "bottom-left":
                    x = 30
                    y = rect.height - 30
                elif position == "bottom-center":
                    x = rect.width / 2 - 20
                    y = rect.height - 30
                elif position == "top-right":
                    x = rect.width - 50
                    y = 30
                elif position == "top-left":
                    x = 30
                    y = 30
                elif position == "top-center":
                    x = rect.width / 2 - 20
                    y = 30
                else:
                    x = rect.width - 50
                    y = rect.height - 30
                
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=10,
                    color=(0, 0, 0)
                )
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error adding page numbers: {e}")
            return False
    
    def remove_pages(self, input_path, output_path, pages_to_remove):
        """
        Remove pages from PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            pages_to_remove (list): List of page numbers to remove (1-indexed)
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            # Convert to 0-indexed and sort in reverse order
            pages_to_delete = sorted([p - 1 for p in pages_to_remove], reverse=True)
            
            for page_num in pages_to_delete:
                if 0 <= page_num < len(doc):
                    doc.delete_page(page_num)
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error removing pages: {e}")
            return False
    
    def rearrange_pages(self, input_path, output_path, new_order):
        """
        Rearrange PDF pages
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            new_order (list): New page order (1-indexed)
            
        Returns:
            bool: Success status
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page_num in new_order:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True
        except Exception as e:
            print(f"Error rearranging pages: {e}")
            return False
    
    def extract_text(self, input_path, use_ocr=False):
        """
        Extract text from PDF
        
        Args:
            input_path (str): Input PDF path
            use_ocr (bool): Use OCR for scanned documents
            
        Returns:
            str: Extracted text
        """
        try:
            doc = fitz.open(input_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
                text += "\n\n--- Page Break ---\n\n"
            
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def extract_images(self, input_path, output_dir, format='jpg'):
        """
        Extract images from PDF
        
        Args:
            input_path (str): Input PDF path
            output_dir (str): Output directory for images
            format (str): Output image format
            
        Returns:
            list: List of extracted image paths
        """
        try:
            doc = fitz.open(input_path)
            image_paths = []
            image_count = 0
            
            for page_num, page in enumerate(doc):
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image_count += 1
                    image_path = os.path.join(output_dir, f"image_{image_count}.{format}")
                    
                    # Convert and save image
                    image = Image.open(io.BytesIO(image_bytes))
                    if format.lower() == 'jpg':
                        image = image.convert('RGB')
                    image.save(image_path)
                    image_paths.append(image_path)
            
            doc.close()
            return image_paths
        except Exception as e:
            print(f"Error extracting images: {e}")
            return []
    
    def compress_pdf(self, input_path, output_path, quality='medium'):
        """
        Compress PDF file
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            quality (str): Compression quality ('low', 'medium', 'high')
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            # Set compression parameters based on quality
            if quality == 'low':
                garbage = 4
                deflate = True
                clean = True
            elif quality == 'high':
                garbage = 1
                deflate = False
                clean = False
            else:  # medium
                garbage = 3
                deflate = True
                clean = True
            
            doc.save(
                output_path,
                garbage=garbage,
                deflate=deflate,
                clean=clean
            )
            doc.close()
            return True
        except Exception as e:
            print(f"Error compressing PDF: {e}")
            return False
    
    def protect_pdf(self, input_path, output_path, password, permissions=None):
        """
        Add password protection to PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            password (str): Password to set
            permissions (dict): Permission settings
            
        Returns:
            bool: Success status
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True
        except Exception as e:
            print(f"Error protecting PDF: {e}")
            return False
    
    def unlock_pdf(self, input_path, output_path, password):
        """
        Remove password protection from PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            password (str): Password to unlock
            
        Returns:
            bool: Success status
        """
        try:
            reader = PdfReader(input_path)
            
            if reader.is_encrypted:
                reader.decrypt(password)
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True
        except Exception as e:
            print(f"Error unlocking PDF: {e}")
            return False
    
    def redact_text(self, input_path, output_path, text_to_redact):
        """
        Redact (black out) specific text in PDF
        
        Args:
            input_path (str): Input PDF path
            output_path (str): Output PDF path
            text_to_redact (str): Text to redact
            
        Returns:
            bool: Success status
        """
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                # Search for the text
                text_instances = page.search_for(text_to_redact)
                
                for inst in text_instances:
                    # Add redaction annotation
                    page.add_redact_annot(inst, fill=(0, 0, 0))
                
                # Apply redactions
                page.apply_redactions()
            
            doc.save(output_path)
            doc.close()
            return True
        except Exception as e:
            print(f"Error redacting PDF: {e}")
            return False
    
    def get_pdf_info(self, input_path):
        """
        Get PDF document information
        
        Args:
            input_path (str): Input PDF path
            
        Returns:
            dict: PDF information
        """
        try:
            doc = fitz.open(input_path)
            metadata = doc.metadata
            
            info = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'keywords': metadata.get('keywords', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc),
                'file_size': os.path.getsize(input_path),
                'is_encrypted': doc.is_encrypted,
                'pages': []
            }
            
            for i, page in enumerate(doc):
                rect = page.rect
                info['pages'].append({
                    'page_number': i + 1,
                    'width': rect.width,
                    'height': rect.height,
                    'rotation': page.rotation
                })
            
            doc.close()
            return info
        except Exception as e:
            print(f"Error getting PDF info: {e}")
            return None


# ============================================================
# Additional utility functions
# ============================================================

def validate_pdf(file_path):
    """Validate if file is a valid PDF"""
    try:
        doc = fitz.open(file_path)
        pages = len(doc)
        doc.close()
        return pages > 0
    except:
        return False


def get_page_count(file_path):
    """Get total page count of PDF"""
    try:
        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return count
    except:
        return 0
