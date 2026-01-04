"""
PDFMaster Test Suite - Tests all PDF operations
"""

import requests
import os
import sys

BASE_URL = "http://localhost:5000"
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def create_test_pdfs():
    """Create test PDF files"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create test PDF 1 (2 pages)
        pdf1_path = os.path.join(TEST_DIR, "test1.pdf")
        c = canvas.Canvas(pdf1_path, pagesize=letter)
        c.drawString(100, 700, 'Test PDF Document 1')
        c.drawString(100, 680, 'This is page 1 of test document 1')
        c.showPage()
        c.drawString(100, 700, 'Test PDF Document 1 - Page 2')
        c.drawString(100, 680, 'This is page 2 of test document 1')
        c.save()
        
        # Create test PDF 2
        pdf2_path = os.path.join(TEST_DIR, "test2.pdf")
        c = canvas.Canvas(pdf2_path, pagesize=letter)
        c.drawString(100, 700, 'Test PDF Document 2')
        c.drawString(100, 680, 'This is page 1 of test document 2')
        c.save()
        
        print("✅ Test PDFs created successfully")
        return pdf1_path, pdf2_path
    except Exception as e:
        print(f"❌ Failed to create test PDFs: {e}")
        return None, None

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Health check: PASSED")
            return True
        else:
            print(f"❌ Health check: FAILED - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check: FAILED - {e}")
        return False

def test_merge(pdf1_path, pdf2_path):
    """Test merge operation"""
    try:
        files = [
            ('files', open(pdf1_path, 'rb')),
            ('files', open(pdf2_path, 'rb'))
        ]
        response = requests.post(f"{BASE_URL}/api/pdf/merge", files=files)
        for f in files:
            f[1].close()
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Merge PDFs: PASSED")
            return True
        else:
            print(f"❌ Merge PDFs: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Merge PDFs: FAILED - {e}")
        return False

def test_split(pdf1_path):
    """Test split operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'pages': '1'}
            response = requests.post(f"{BASE_URL}/api/pdf/split", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Split PDF: PASSED")
            return True
        else:
            print(f"❌ Split PDF: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Split PDF: FAILED - {e}")
        return False

def test_rotate(pdf1_path):
    """Test rotate operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'angle': '90'}
            response = requests.post(f"{BASE_URL}/api/pdf/rotate", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Rotate PDF: PASSED")
            return True
        else:
            print(f"❌ Rotate PDF: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Rotate PDF: FAILED - {e}")
        return False

def test_compress(pdf1_path):
    """Test compress operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'quality': 'medium'}
            response = requests.post(f"{BASE_URL}/api/pdf/compress", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Compress PDF: PASSED")
            return True
        else:
            print(f"❌ Compress PDF: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Compress PDF: FAILED - {e}")
        return False

def test_watermark(pdf1_path):
    """Test watermark operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'text': 'CONFIDENTIAL', 'opacity': '0.3'}
            response = requests.post(f"{BASE_URL}/api/pdf/watermark", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Watermark PDF: PASSED")
            return True
        else:
            print(f"❌ Watermark PDF: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Watermark PDF: FAILED - {e}")
        return False

def test_extract_text(pdf1_path):
    """Test extract text operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/pdf/extract-text", files=files)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Extract Text: PASSED")
            return True
        else:
            print(f"❌ Extract Text: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Extract Text: FAILED - {e}")
        return False

def test_extract_images(pdf1_path):
    """Test extract images operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/pdf/extract-images", files=files)
        
        # May return success with 0 images if no images in PDF
        # Or return failure because our test PDF has no images - that's OK
        if response.status_code == 200:
            print("✅ Extract Images: PASSED")
            return True
        else:
            # Check if it's just "no images found" which is expected for our test PDF
            resp_json = response.json()
            if "No images found" in resp_json.get("message", ""):
                print("✅ Extract Images: PASSED (no images in test PDF - expected)")
                return True
            print(f"❌ Extract Images: FAILED - {resp_json}")
            return False
    except Exception as e:
        print(f"❌ Extract Images: FAILED - {e}")
        return False

def test_page_numbers(pdf1_path):
    """Test add page numbers operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'format': '{page}/{total}', 'position': 'bottom-right'}
            response = requests.post(f"{BASE_URL}/api/pdf/page-numbers", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Page Numbers: PASSED")
            return True
        else:
            print(f"❌ Page Numbers: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Page Numbers: FAILED - {e}")
        return False

def test_protect(pdf1_path):
    """Test protect PDF operation"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            data = {'password': 'test123'}
            response = requests.post(f"{BASE_URL}/api/security/protect", files=files, data=data)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ Protect PDF: PASSED")
            return True
        else:
            print(f"❌ Protect PDF: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Protect PDF: FAILED - {e}")
        return False

def test_pdf_to_jpg(pdf1_path):
    """Test PDF to JPG conversion"""
    try:
        with open(pdf1_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/convert/pdf-to-jpg", files=files)
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ PDF to JPG: PASSED")
            return True
        else:
            print(f"❌ PDF to JPG: FAILED - {response.json()}")
            return False
    except Exception as e:
        print(f"❌ PDF to JPG: FAILED - {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("    PDFMaster API Test Suite")
    print("="*50 + "\n")
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start the server first.")
        print("Run: python app.py")
        return
    
    print()
    
    # Create test files
    pdf1_path, pdf2_path = create_test_pdfs()
    if not pdf1_path:
        return
    
    print("\n--- Testing PDF Operations ---\n")
    
    results = []
    results.append(("Merge PDFs", test_merge(pdf1_path, pdf2_path)))
    results.append(("Split PDF", test_split(pdf1_path)))
    results.append(("Rotate PDF", test_rotate(pdf1_path)))
    results.append(("Compress PDF", test_compress(pdf1_path)))
    results.append(("Watermark PDF", test_watermark(pdf1_path)))
    results.append(("Extract Text", test_extract_text(pdf1_path)))
    results.append(("Extract Images", test_extract_images(pdf1_path)))
    results.append(("Page Numbers", test_page_numbers(pdf1_path)))
    results.append(("Protect PDF", test_protect(pdf1_path)))
    results.append(("PDF to JPG", test_pdf_to_jpg(pdf1_path)))
    
    # Summary
    print("\n" + "="*50)
    print("    Test Summary")
    print("="*50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed:")
        for name, result in results:
            if not result:
                print(f"   - {name}")

if __name__ == "__main__":
    run_all_tests()
