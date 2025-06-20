import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

# Try multiple PDF to Excel conversion methods
conversion_methods = []

# Method 1: tabula-py (best for table extraction)
try:
    import tabula
    conversion_methods.append("tabula")
    print("✅ Tabula-py available (best for tables)")
except ImportError:
    print("⚠️ Tabula-py not found")

# Method 2: pdfplumber (good for structured data)
try:
    import pdfplumber
    conversion_methods.append("pdfplumber")
    print("✅ PDFplumber available")
except ImportError:
    print("⚠️ PDFplumber not found")

# Method 3: camelot (specialized for tables)
try:
    import camelot
    conversion_methods.append("camelot")
    print("✅ Camelot available (table specialist)")
except ImportError:
    print("⚠️ Camelot not found")

# Method 4: PyMuPDF as fallback
try:
    import fitz
    conversion_methods.append("pymupdf")
    print("✅ PyMuPDF available (fallback)")
except ImportError:
    print("⚠️ PyMuPDF not found")

if not conversion_methods:
    print("❌ No PDF conversion libraries found!")
    print("\nInstall one of these:")
    print("  pip install tabula-py              # Best for tables")
    print("  pip install pdfplumber             # Good general purpose")
    print("  pip install camelot-py[cv]         # Table specialist")
    print("  pip install pymupdf                # Basic fallback")
    exit(1)

# --- CONFIG ---
URL = (
    "https://www.canada.ca/en/health-canada/services/"
    "drugs-health-products/drug-products/drug-product-database/"
    "label-safety-assessment-update/product-monograph-brand-safety-updates.html"
)
SAVE_DIR = "downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

def clean_filename(text):
    """Clean and sanitize filename"""
    text = text.strip().lower()
    text = re.sub(r"[\\/*?\"<>|\r\n]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-zA-Z0-9_]", "", text)
    return text[:80]

def convert_with_tabula(pdf_path, excel_path):
    """Convert PDF to Excel using tabula-py (best for tables)"""
    try:
        print("📊 Using Tabula for table extraction...")
        
        # Extract all tables from all pages
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        if not tables:
            print("⚠️ No tables found with Tabula")
            return False
        
        print(f"✅ Found {len(tables)} table(s) with Tabula")
        
        # Save to Excel with multiple sheets if multiple tables
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                if not table.empty:
                    sheet_name = f'Table_{i+1}' if len(tables) > 1 else 'Data'
                    table.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"📋 Saved table {i+1}: {table.shape[0]} rows, {table.shape[1]} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Tabula conversion failed: {e}")
        return False

def convert_with_pdfplumber(pdf_path, excel_path):
    """Convert PDF to Excel using pdfplumber"""
    try:
        print("📄 Using PDFplumber for extraction...")
        
        all_data = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                print(f"📖 Processing page {page_num + 1}/{len(pdf.pages)}")
                
                # Try to extract tables first
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        # Filter out empty rows and clean data
                        for row in table:
                            if row and any(cell for cell in row if cell and str(cell).strip()):
                                clean_row = [str(cell).strip() if cell else "" for cell in row]
                                all_data.append(clean_row)
                else:
                    # If no tables, try text extraction with structure
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.lower().startswith(('page ', 'confidential')):
                                # Try to detect columns by multiple spaces
                                cells = re.split(r'\s{2,}', line)
                                cells = [cell.strip() for cell in cells if cell.strip()]
                                if len(cells) > 1:  # Multi-column data
                                    all_data.append(cells)
        
        if all_data:
            # Create DataFrame and save
            max_cols = max(len(row) for row in all_data)
            padded_data = [row + [''] * (max_cols - len(row)) for row in all_data]
            
            df = pd.DataFrame(padded_data)
            df.to_excel(excel_path, index=False, header=False)
            print(f"✅ PDFplumber extracted {len(all_data)} rows")
            return True
        else:
            print("⚠️ No data extracted with PDFplumber")
            return False
            
    except Exception as e:
        print(f"❌ PDFplumber conversion failed: {e}")
        return False

def convert_with_camelot(pdf_path, excel_path):
    """Convert PDF to Excel using camelot (table specialist)"""
    try:
        print("🐪 Using Camelot for table extraction...")
        
        # Extract tables from all pages
        tables = camelot.read_pdf(pdf_path, pages='all')
        
        if len(tables) == 0:
            print("⚠️ No tables found with Camelot")
            return False
        
        print(f"✅ Found {len(tables)} table(s) with Camelot")
        
        # Save to Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                if not table.df.empty:
                    sheet_name = f'Table_{i+1}' if len(tables) > 1 else 'Data'
                    table.df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"📋 Saved table {i+1}: {table.df.shape[0]} rows, {table.df.shape[1]} columns")
                    print(f"   Accuracy: {table.accuracy:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Camelot conversion failed: {e}")
        return False

def convert_with_pymupdf(pdf_path, excel_path):
    """Convert PDF to Excel using PyMuPDF (fallback)"""
    try:
        print("📜 Using PyMuPDF for extraction...")
        
        doc = fitz.open(pdf_path)
        all_data = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Try table detection first
            try:
                tables = page.find_tables()
                if tables:
                    for table in tables:
                        table_data = table.extract()
                        for row in table_data:
                            if row and any(cell for cell in row if cell):
                                clean_row = [str(cell).strip() if cell else "" for cell in row]
                                all_data.append(clean_row)
                    continue
            except:
                pass
            
            # Fallback to text extraction
            text = page.get_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith(('page ', 'confidential')):
                        cells = re.split(r'\s{2,}', line)
                        cells = [cell.strip() for cell in cells if cell.strip()]
                        if len(cells) > 1:
                            all_data.append(cells)
        
        doc.close()
        
        if all_data:
            max_cols = max(len(row) for row in all_data)
            padded_data = [row + [''] * (max_cols - len(row)) for row in all_data]
            
            df = pd.DataFrame(padded_data)
            df.to_excel(excel_path, index=False, header=False)
            print(f"✅ PyMuPDF extracted {len(all_data)} rows")
            return True
        else:
            print("⚠️ No data extracted with PyMuPDF")
            return False
            
    except Exception as e:
        print(f"❌ PyMuPDF conversion failed: {e}")
        return False

def convert_pdf_to_excel(pdf_path, excel_path):
    """Try multiple conversion methods in order of preference"""
    
    # Order of preference: tabula > camelot > pdfplumber > pymupdf
    conversion_functions = {
        'tabula': convert_with_tabula,
        'camelot': convert_with_camelot,
        'pdfplumber': convert_with_pdfplumber,
        'pymupdf': convert_with_pymupdf
    }
    
    for method in ['tabula', 'camelot', 'pdfplumber', 'pymupdf']:
        if method in conversion_methods:
            print(f"\n🔄 Trying {method}...")
            if conversion_functions[method](pdf_path, excel_path):
                print(f"✅ Successfully converted with {method}")
                return True
            else:
                print(f"❌ {method} failed, trying next method...")
    
    return False

def log_failure(pdf_path, error_type, error_msg=""):
    """Log failed PDF processing"""
    with open("failed_pdfs.txt", "a", encoding='utf-8') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {error_type}: {pdf_path}")
        if error_msg:
            log_file.write(f" - {error_msg}")
        log_file.write("\n")

# --- STEP 1: Scrape PDF links ---
print("🔍 Scraping PDF links from Health Canada website...")
try:
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"❌ Failed to access website: {e}")
    exit(1)

soup = BeautifulSoup(response.text, "html.parser")
pdf_links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.lower().endswith(".pdf"):
        full_url = href if href.startswith("http") else f"https://www.canada.ca{href}"
        label = clean_filename(a.text or "document")
        pdf_links.append({"url": full_url, "label": label})

print(f"🔍 Found {len(pdf_links)} PDF files.")

if not pdf_links:
    print("⚠️ No PDF links found. The website structure might have changed.")
    exit(1)

# --- STEP 2: Download and Convert PDFs ---
successful_count = 0
failed_count = 0

for i, item in enumerate(pdf_links, 1):
    url = item["url"]
    label = item["label"]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pdf_path = os.path.join(SAVE_DIR, f"{label}_{timestamp}.pdf")
    excel_path = os.path.join(SAVE_DIR, f"{label}_{timestamp}.xlsx")

    print(f"\n📄 Processing {i}/{len(pdf_links)}: {label}")
    print(f"=" * 60)

    # ---- DOWNLOAD ----
    try:
        print(f"⬇️ Downloading: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        
        with open(pdf_path, 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded: {os.path.basename(pdf_path)} ({len(r.content):,} bytes)")
        
    except requests.exceptions.Timeout:
        print(f"⏰ Download timeout: {url}")
        log_failure(pdf_path, "DownloadTimeout")
        failed_count += 1
        continue
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        log_failure(pdf_path, "DownloadError", str(e))
        failed_count += 1
        continue

    # ---- CONVERT TO EXCEL ----
    if convert_pdf_to_excel(pdf_path, excel_path):
        print(f"📁 Excel saved: {os.path.basename(excel_path)}")
        successful_count += 1
    else:
        print(f"❌ All conversion methods failed")
        log_failure(pdf_path, "ConversionFailed")
        failed_count += 1

    # Optional: Remove PDF after conversion to save space
    # os.remove(pdf_path)

    time.sleep(1)  # Be polite to the server

# --- SUMMARY ---
print(f"\n" + "=" * 60)
print(f"🎉 PROCESSING COMPLETE!")
print(f"✅ Successfully processed: {successful_count}")
print(f"❌ Failed: {failed_count}")
print(f"📂 Files saved to: {os.path.abspath(SAVE_DIR)}")

if failed_count > 0:
    print(f"📋 Check 'failed_pdfs.txt' for details on failed files")

# Installation recommendations
print(f"\n💡 RECOMMENDATIONS:")
if 'tabula' not in conversion_methods:
    print("   pip install tabula-py              # Best for table extraction")
if 'camelot' not in conversion_methods:
    print("   pip install camelot-py[cv]         # Specialized table extraction")
if 'pdfplumber' not in conversion_methods:
    print("   pip install pdfplumber             # Good general extraction")

print(f"\n📊 Available methods: {', '.join(conversion_methods)}")



# import os
# import re
# import requests
# import pytesseract
# import fitz  # PyMuPDF
# import camelot
# import pdfplumber
# import pandas as pd
# from datetime import datetime
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from tempfile import TemporaryDirectory

# # CONFIGURATION
# BASE_URL = "https://www.canada.ca"
# PAGE_URL = urljoin(BASE_URL, "/en/health-canada/services/drugs-health-products/drug-products/drug-product-database/label-safety-assessment-update/product-monograph-brand-safety-updates.html")
# DOWNLOAD_DIR = "downloads"
# TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update if different

# # Ensure Tesseract is set
# if os.path.exists(TESSERACT_PATH):
#     pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
# else:
#     print("⚠️ Tesseract not found. OCR may fail.")

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# def sanitize_filename(name):
#     return re.sub(r'[\\/*?:"<>|]', "_", name)

# def get_pdf_links(page_url):
#     res = requests.get(page_url)
#     soup = BeautifulSoup(res.content, 'html.parser')
#     return [urljoin(BASE_URL, link['href']) for link in soup.find_all('a', href=True) if link['href'].lower().endswith('.pdf')]

# def download_pdf(url, save_folder):
#     file_name = sanitize_filename(url.split('/')[-1])
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     full_name = f"{file_name}_{timestamp}.pdf"
#     file_path = os.path.join(save_folder, full_name)

#     try:
#         res = requests.get(url)
#         res.raise_for_status()
#         with open(file_path, 'wb') as f:
#             f.write(res.content)
#         print(f"✅ Downloaded: {file_path} ({len(res.content):,} bytes)")
#         return file_path
#     except Exception as e:
#         print(f"❌ Failed to download {url}: {e}")
#         return None

# def try_camelot(pdf_path):
#     try:
#         print("🐪 Using Camelot for table extraction...")
#         tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
#         if tables:
#             df = pd.concat([t.df for t in tables])
#             print(f"✅ Found {len(tables)} table(s) with Camelot")
#             return df
#     except Exception as e:
#         print(f"❌ Camelot failed: {e}")
#     return None

# def try_pdfplumber(pdf_path):
#     try:
#         print("🔍 Trying PDFPlumber...")
#         with pdfplumber.open(pdf_path) as pdf:
#             all_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
#         return pd.DataFrame({'Text': all_text})
#     except Exception as e:
#         print(f"❌ PDFPlumber failed: {e}")
#     return None

# def try_ocr(pdf_path):
#     try:
#         print("🧠 Using OCR...")
#         with TemporaryDirectory() as temp_dir:
#             doc = fitz.open(pdf_path)
#             all_text = []
#             for i, page in enumerate(doc):
#                 pix = page.get_pixmap(dpi=300)
#                 img_path = os.path.join(temp_dir, f"page_{i}.png")
#                 pix.save(img_path)
#                 text = pytesseract.image_to_string(img_path)
#                 all_text.append(text)
#             return pd.DataFrame({'OCR_Text': all_text})
#     except Exception as e:
#         print(f"❌ OCR failed: {e}")
#     return None

# def convert_pdf_to_excel(pdf_path):
#     for extractor in [try_camelot, try_pdfplumber, try_ocr]:
#         df = extractor(pdf_path)
#         if df is not None and not df.empty:
#             excel_path = pdf_path.replace(".pdf", ".xlsx")
#             df.to_excel(excel_path, index=False)
#             print(f"📁 Excel saved: {excel_path}")
#             return True
#     print(f"❌ Failed to extract data from: {pdf_path}")
#     return False

# def main():
#     print(f"🔍 Fetching PDF links from {PAGE_URL}")
#     pdf_links = get_pdf_links(PAGE_URL)
#     print(f"📄 Found {len(pdf_links)} PDF files.")

#     success, failed = 0, 0
#     for link in pdf_links:
#         print(f"\n⬇️ Downloading: {link}")
#         pdf_file = download_pdf(link, DOWNLOAD_DIR)
#         if pdf_file:
#             if convert_pdf_to_excel(pdf_file):
#                 success += 1
#             else:
#                 failed += 1

#     print("\n" + "=" * 60)
#     print("🎉 PROCESSING COMPLETE!")
#     print(f"✅ Successfully processed: {success}")
#     print(f"❌ Failed: {failed}")
#     print(f"📂 Files saved to: {os.path.abspath(DOWNLOAD_DIR)}")

# if __name__ == "__main__":
#     main()
