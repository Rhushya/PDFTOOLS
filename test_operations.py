# PDF Operations Test Suite
# File: test_operations.py

import requests
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time
from PIL import Image

BASE_URL = "http://localhost:5000"

def create_test_pdf(filename, num_pages=3):
    """Create a test PDF file"""
    c = canvas.Canvas(filename, pagesize=letter)
    for i in range(num_pages):
        c.drawString(100, 700, f"Test PDF Page {i+1}")
        c.drawString(100, 680, f"This is sample content for testing.")
        if i < num_pages - 1:
            c.showPage()
    c.save()
    return filename

def create_test_image(filename, size=(200, 200), color='red'):
    """Create a test image"""
    img = Image.new('RGB', size, color)
    img.save(filename)
    return filename

def test_merge():
    """Test PDF merge operation"""
    pdf1 = create_test_pdf("test_merge_1.pdf", 1)
    pdf2 = create_test_pdf("test_merge_2.pdf", 1)
    
    try:
        with open(pdf1, 'rb') as f1, open(pdf2, 'rb') as f2:
            response = requests.post(
                f"{BASE_URL}/api/pdf/merge",
                files=[('files', f1), ('files', f2)]
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Merge successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        for f in [pdf1, pdf2]:
            if os.path.exists(f):
                os.remove(f)

def test_split():
    """Test PDF split operation"""
    pdf = create_test_pdf("test_split.pdf", 3)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/pdf/split",
                files={'file': f},
                data={'pages': '1-2'}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Split successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_rotate():
    """Test PDF rotate operation"""
    pdf = create_test_pdf("test_rotate.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/pdf/rotate",
                files={'file': f},
                data={'angle': '90'}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Rotate successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_compress():
    """Test PDF compress operation"""
    pdf = create_test_pdf("test_compress.pdf", 2)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/pdf/compress",
                files={'file': f}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Compress successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_watermark():
    """Test PDF watermark operation"""
    pdf = create_test_pdf("test_watermark.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/pdf/watermark",
                files={'file': f},
                data={'text': 'TEST WATERMARK'}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Watermark successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_extract_text():
    """Test PDF text extraction"""
    pdf = create_test_pdf("test_extract.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/pdf/extract-text",
                files={'file': f}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Extract text successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_pdf_to_jpg():
    """Test PDF to JPG conversion"""
    pdf = create_test_pdf("test_tojpg.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/convert/pdf-to-jpg",
                files={'file': f}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "PDF to JPG successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_pdf_to_png():
    """Test PDF to PNG conversion"""
    pdf = create_test_pdf("test_topng.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/convert/pdf-to-png",
                files={'file': f}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "PDF to PNG successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)

def test_jpg_to_pdf():
    """Test JPG to PDF conversion"""
    img = create_test_image("test_image.jpg", color='blue')
    
    try:
        with open(img, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/convert/image-to-pdf",
                files={'files': f}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "JPG to PDF successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(img):
            os.remove(img)

def test_protect():
    """Test PDF protection"""
    pdf = create_test_pdf("test_protect.pdf", 1)
    
    try:
        with open(pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/security/protect",
                files={'file': f},
                data={'password': 'testpassword'}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Protect successful"
            else:
                return False, data.get('message', 'Unknown error')
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(pdf):
            os.remove(pdf)


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Merge PDFs", test_merge),
        ("Split PDF", test_split),
        ("Rotate PDF", test_rotate),
        ("Compress PDF", test_compress),
        ("Add Watermark", test_watermark),
        ("Extract Text", test_extract_text),
        ("PDF to JPG", test_pdf_to_jpg),
        ("PDF to PNG", test_pdf_to_png),
        ("Images to PDF", test_jpg_to_pdf),
        ("Protect PDF", test_protect),
    ]
    
    print("\n" + "=" * 60)
    print("  PDFMaster Operations Test Suite")
    print("=" * 60)
    
    results = []
    for name, test_func in tests:
        print(f"\n▶ Testing: {name}...", end=" ")
        try:
            success, message = test_func()
            results.append((name, success, message))
            if success:
                print(f"✅ PASS")
            else:
                print(f"❌ FAIL")
                print(f"  → {message}")
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"❌ ERROR")
            print(f"  → {e}")
    
    # Summary
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! PDFMaster is working correctly.\n")
    else:
        print("\n⚠️  Some tests failed. See details above.\n")
        for name, success, message in results:
            if not success:
                print(f"  • {name}: {message}")
    
    return passed, total

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Connecting to server at", BASE_URL)
    time.sleep(1)
    run_all_tests()
