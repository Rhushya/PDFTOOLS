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
    Returns dict with 'success' key for all operations
    """
    
    def __init__(self):
        self.supported_operations = [
            'merge', 'split', 'rotate', 'crop', 'compress',
            'watermark', 'extract_text', 'extract_images',
            'add_page_numbers', 'remove_pages', 'rearrange',
            'protect', 'unlock', 'redact'
        ]
    
    def merge_pdfs(self, input_files, output_path):
        """Merge multiple PDFs into a single document"""
        try:
            merger = PdfMerger()
            
            for pdf_file in input_files:
                if os.path.exists(pdf_file):
                    merger.append(pdf_file)
            
            merger.write(output_path)
            merger.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def split_pdf(self, input_path, output_dir, pages_str):
        """Extract specific pages from PDF"""
        try:
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            output_files = []
            
            # Parse pages string (e.g., "1-3" or "1,3,5")
            pages = []
            if pages_str:
                if '-' in pages_str:
                    start, end = pages_str.split('-')
                    pages = list(range(int(start), int(end) + 1))
                elif ',' in pages_str:
                    pages = [int(p.strip()) for p in pages_str.split(',')]
                else:
                    pages = [int(pages_str)]
            else:
                pages = list(range(1, total_pages + 1))
            
            for page_num in pages:
                if 1 <= page_num <= total_pages:
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])
                    
                    output_file = os.path.join(output_dir, f"page_{page_num}.pdf")
                    with open(output_file, 'wb') as f:
                        writer.write(f)
                    output_files.append(output_file)
            
            return {'success': True, 'pages': output_files, 'page_count': len(output_files)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rotate_pdf(self, input_path, output_path, angle, pages=None):
        """Rotate PDF pages"""
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
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def compress_pdf(self, input_path, output_path, quality='medium', target_reduction=None):
        """
        Compress PDF file with flexible compression options
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            quality: 'low' (max compression), 'medium', 'high' (minimal compression)
            target_reduction: Optional target reduction percentage (10-90)
        """
        try:
            original_size = os.path.getsize(input_path)
            doc = fitz.open(input_path)
            
            # Set compression parameters based on quality or target_reduction
            if target_reduction:
                # Map target reduction to compression settings
                reduction_pct = min(max(int(target_reduction), 10), 90)
                if reduction_pct >= 70:
                    garbage = 4
                    deflate = True
                    clean = True
                    image_quality = 30
                elif reduction_pct >= 50:
                    garbage = 3
                    deflate = True
                    clean = True
                    image_quality = 50
                elif reduction_pct >= 30:
                    garbage = 2
                    deflate = True
                    clean = False
                    image_quality = 70
                else:
                    garbage = 1
                    deflate = True
                    clean = False
                    image_quality = 85
            elif quality == 'low':  # Maximum compression
                garbage = 4
                deflate = True
                clean = True
                image_quality = 30
            elif quality == 'high':  # Minimal compression, best quality
                garbage = 1
                deflate = False
                clean = False
                image_quality = 95
            else:  # medium - balanced
                garbage = 3
                deflate = True
                clean = True
                image_quality = 60
            
            # Compress images in the PDF for better compression
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        if base_image:
                            image_bytes = base_image["image"]
                            image = Image.open(io.BytesIO(image_bytes))
                            
                            # Compress image
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            img_buffer = io.BytesIO()
                            image.save(img_buffer, format='JPEG', quality=image_quality, optimize=True)
                            
                            # Replace image in PDF
                            doc.xref_set_key(xref, "Filter", fitz.PDF_NAME_DCTDecode)
                            doc.update_stream(xref, img_buffer.getvalue())
                    except:
                        # Skip if image can't be processed
                        continue
            
            doc.save(output_path, garbage=garbage, deflate=deflate, clean=clean)
            doc.close()
            
            compressed_size = os.path.getsize(output_path)
            reduction = round((1 - compressed_size / original_size) * 100, 2)
            
            return {
                'success': True,
                'output_path': output_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'reduction': f"{reduction}%"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_watermark(self, input_path, output_path, text, opacity=0.3, angle=45, color=(0.5, 0.5, 0.5)):
        """Add watermark to PDF"""
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                rect = page.rect
                # Calculate center position
                center = fitz.Point(rect.width / 2, rect.height / 2)
                
                # Create watermark with gray color based on opacity
                gray_value = 1 - (opacity * 0.5)
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
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_page_numbers(self, input_path, output_path, position="bottom-center", start_number=1):
        """Add page numbers to PDF"""
        try:
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            for i, page in enumerate(doc):
                rect = page.rect
                page_num = start_number + i
                text = f"{page_num}"
                
                # Calculate position
                if position == "bottom-right":
                    x = rect.width - 50
                    y = rect.height - 30
                elif position == "bottom-left":
                    x = 30
                    y = rect.height - 30
                elif position == "bottom-center":
                    x = rect.width / 2 - 10
                    y = rect.height - 30
                elif position == "top-right":
                    x = rect.width - 50
                    y = 30
                elif position == "top-left":
                    x = 30
                    y = 30
                elif position == "top-center":
                    x = rect.width / 2 - 10
                    y = 30
                else:
                    x = rect.width / 2 - 10
                    y = rect.height - 30
                
                page.insert_text(
                    (x, y),
                    text,
                    fontsize=10,
                    color=(0, 0, 0)
                )
            
            doc.save(output_path)
            doc.close()
            return {'success': True, 'output_path': output_path, 'page_count': total_pages}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_text(self, input_path, output_path, output_format='txt'):
        """
        Extract text from PDF and save to file
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output file
            output_format: 'txt' or 'docx'
        """
        try:
            doc = fitz.open(input_path)
            text = ""
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += f"--- Page {page_num + 1} ---\n\n"
                text += page_text
                text += "\n\n"
            
            doc.close()
            text = text.strip()
            
            if not text:
                return {'success': False, 'error': 'No text found in PDF'}
            
            if output_format == 'docx':
                try:
                    from docx import Document
                    document = Document()
                    
                    # Split text into paragraphs
                    for para in text.split('\n\n'):
                        if para.strip():
                            document.add_paragraph(para.strip())
                    
                    document.save(output_path)
                except ImportError:
                    # Fallback to txt if docx not available
                    output_path = output_path.replace('.docx', '.txt')
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text)
            else:
                # Save as txt
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            # Return preview
            preview = text[:500] + "..." if len(text) > 500 else text
            
            return {
                'success': True, 
                'output_path': output_path, 
                'text_preview': preview,
                'char_count': len(text),
                'word_count': len(text.split())
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_images(self, input_path, output_dir, format='jpg'):
        """Extract images from PDF"""
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
            
            if image_count == 0:
                return {'success': False, 'error': 'No images found in PDF'}
            
            return {'success': True, 'images': image_paths, 'image_count': image_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def protect_pdf(self, input_path, output_path, password):
        """Add password protection to PDF"""
        try:
            doc = fitz.open(input_path)
            
            # Encrypt with password
            doc.save(
                output_path,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw=password,
                user_pw=password,
                permissions=(
                    fitz.PDF_PERM_PRINT |
                    fitz.PDF_PERM_COPY |
                    fitz.PDF_PERM_MODIFY
                )
            )
            doc.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unlock_pdf(self, input_path, output_path, password):
        """Remove password protection from PDF"""
        try:
            doc = fitz.open(input_path)
            
            if doc.is_encrypted:
                if not doc.authenticate(password):
                    return {'success': False, 'error': 'Invalid password'}
            
            # Save without encryption
            doc.save(output_path)
            doc.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def crop_pdf(self, input_path, output_path, coordinates):
        """Crop PDF pages"""
        try:
            doc = fitz.open(input_path)
            
            for page in doc:
                rect = fitz.Rect(coordinates)
                page.set_cropbox(rect)
            
            doc.save(output_path)
            doc.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_pages(self, input_path, output_path, pages_to_remove):
        """Remove pages from PDF"""
        try:
            doc = fitz.open(input_path)
            
            # Convert to 0-indexed and sort in reverse order
            pages_to_delete = sorted([p - 1 for p in pages_to_remove], reverse=True)
            
            for page_num in pages_to_delete:
                if 0 <= page_num < len(doc):
                    doc.delete_page(page_num)
            
            doc.save(output_path)
            doc.close()
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rearrange_pages(self, input_path, output_path, new_order):
        """Rearrange PDF pages"""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page_num in new_order:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {'success': True, 'output_path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_tables(self, input_path, output_dir, output_format='txt'):
        """
        Extract tables from PDF
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            output_format: 'txt' or 'markdown'
        """
        try:
            doc = fitz.open(input_path)
            tables_found = []
            all_tables_text = ""
            
            for page_num, page in enumerate(doc):
                # Try to find tables using structured text extraction
                tabs = page.find_tables()
                
                if tabs.tables:
                    for table_idx, table in enumerate(tabs.tables):
                        table_data = table.extract()
                        
                        if table_data:
                            table_name = f"page{page_num + 1}_table{table_idx + 1}"
                            
                            if output_format == 'markdown':
                                # Convert to markdown format
                                md_table = self._table_to_markdown(table_data)
                                all_tables_text += f"## Table from Page {page_num + 1}, Table {table_idx + 1}\n\n"
                                all_tables_text += md_table + "\n\n"
                            else:
                                # Plain text format
                                txt_table = self._table_to_text(table_data)
                                all_tables_text += f"=== Table from Page {page_num + 1}, Table {table_idx + 1} ===\n\n"
                                all_tables_text += txt_table + "\n\n"
                            
                            tables_found.append(table_name)
            
            doc.close()
            
            if not tables_found:
                return {'success': False, 'error': 'No tables found in PDF'}
            
            # Save output
            ext = 'md' if output_format == 'markdown' else 'txt'
            output_path = os.path.join(output_dir, f"tables.{ext}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(all_tables_text)
            
            return {
                'success': True,
                'output_path': output_path,
                'tables_count': len(tables_found),
                'tables': tables_found
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _table_to_markdown(self, table_data):
        """Convert table data to markdown format"""
        if not table_data or not table_data[0]:
            return ""
        
        md_lines = []
        
        # Header row
        header = [str(cell) if cell else "" for cell in table_data[0]]
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # Data rows
        for row in table_data[1:]:
            cells = [str(cell) if cell else "" for cell in row]
            # Pad row if needed
            while len(cells) < len(header):
                cells.append("")
            md_lines.append("| " + " | ".join(cells[:len(header)]) + " |")
        
        return "\n".join(md_lines)
    
    def _table_to_text(self, table_data):
        """Convert table data to plain text format"""
        if not table_data:
            return ""
        
        txt_lines = []
        
        # Calculate column widths
        col_widths = []
        for row in table_data:
            for i, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                while len(col_widths) <= i:
                    col_widths.append(0)
                col_widths[i] = max(col_widths[i], len(cell_str))
        
        # Format rows
        for row in table_data:
            cells = []
            for i, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                if i < len(col_widths):
                    cells.append(cell_str.ljust(col_widths[i]))
                else:
                    cells.append(cell_str)
            txt_lines.append(" | ".join(cells))
        
        return "\n".join(txt_lines)
    
    def pdf_to_images(self, input_path, output_dir, format='jpeg', dpi=150, pages=None):
        """
        Convert PDF pages to images
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output images
            format: 'jpeg' or 'png'
            dpi: Resolution (72-300)
            pages: List of page numbers or None for all pages
        """
        try:
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            # Parse pages if string
            if isinstance(pages, str) and pages:
                if pages.lower() == 'all':
                    pages = None
                elif '-' in pages:
                    start, end = pages.split('-')
                    pages = list(range(int(start), int(end) + 1))
                elif ',' in pages:
                    pages = [int(p.strip()) for p in pages.split(',')]
                else:
                    pages = [int(pages)]
            
            # Validate pages
            if pages:
                pages = [p for p in pages if 1 <= p <= total_pages]
                if not pages:
                    return {'success': False, 'error': f'Invalid page numbers. PDF has {total_pages} pages.'}
            
            output_paths = []
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            
            for i, page in enumerate(doc):
                page_num = i + 1
                if pages is None or page_num in pages:
                    pix = page.get_pixmap(matrix=matrix)
                    
                    if format.lower() == 'jpeg':
                        output_path = os.path.join(output_dir, f"page_{page_num}.jpg")
                        # Convert to PIL for JPEG with quality control
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(output_path, 'JPEG', quality=95)
                    else:
                        output_path = os.path.join(output_dir, f"page_{page_num}.png")
                        pix.save(output_path)
                    
                    output_paths.append(output_path)
            
            doc.close()
            
            if not output_paths:
                return {'success': False, 'error': 'No pages converted'}
            
            return {
                'success': True,
                'images': output_paths,
                'page_count': len(output_paths),
                'total_pages': total_pages
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Utility functions
def validate_pdf(file_path):
    """Check if a file is a valid PDF"""
    try:
        doc = fitz.open(file_path)
        is_valid = doc.page_count > 0
        doc.close()
        return is_valid
    except:
        return False


def get_page_count(file_path):
    """Get the number of pages in a PDF"""
    try:
        doc = fitz.open(file_path)
        count = doc.page_count
        doc.close()
        return count
    except:
        return 0
