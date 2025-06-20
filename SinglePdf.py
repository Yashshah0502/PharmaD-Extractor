# # # import os
# # # import re
# # # import time
# # # import requests
# # # from bs4 import BeautifulSoup
# # # from datetime import datetime
# # # import pandas as pd

# # # # Try multiple PDF to Excel conversion methods
# # # conversion_methods = []

# # # # Method 1: tabula-py (best for table extraction)
# # # try:
# # #     import tabula
# # #     conversion_methods.append("tabula")
# # #     print("✅ Tabula-py available (best for tables)")
# # # except ImportError:
# # #     print("⚠️ Tabula-py not found")

# # # # Method 2: pdfplumber (good for structured data)
# # # try:
# # #     import pdfplumber
# # #     conversion_methods.append("pdfplumber")
# # #     print("✅ PDFplumber available")
# # # except ImportError:
# # #     print("⚠️ PDFplumber not found")

# # # # Method 3: camelot (specialized for tables)
# # # try:
# # #     import camelot
# # #     conversion_methods.append("camelot")
# # #     print("✅ Camelot available (table specialist)")
# # # except ImportError:
# # #     print("⚠️ Camelot not found")

# # # # Method 4: PyMuPDF as fallback
# # # try:
# # #     import fitz
# # #     conversion_methods.append("pymupdf")
# # #     print("✅ PyMuPDF available (fallback)")
# # # except ImportError:
# # #     print("⚠️ PyMuPDF not found")

# # # if not conversion_methods:
# # #     print("❌ No PDF conversion libraries found!")
# # #     print("\nInstall one of these:")
# # #     print("  pip install tabula-py              # Best for tables")
# # #     print("  pip install pdfplumber             # Good general purpose")
# # #     print("  pip install camelot-py[cv]         # Table specialist")
# # #     print("  pip install pymupdf                # Basic fallback")
# # #     exit(1)

# # # # --- CONFIG ---
# # # URL = "https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/applications-submissions/register-innovative-drugs.html"
# # # SAVE_DIR = "innovative_drugs_downloads"
# # # os.makedirs(SAVE_DIR, exist_ok=True)

# # # def clean_filename(text):
# # #     """Clean and sanitize filename"""
# # #     text = text.strip().lower()
# # #     text = re.sub(r"[\\/*?\"<>|\r\n]", "", text)
# # #     text = re.sub(r"\s+", "_", text)
# # #     text = re.sub(r"[^a-zA-Z0-9_]", "", text)
# # #     return text[:80]

# # # def is_drug_related_pdf(url, link_text, context_text=""):
# # #     """
# # #     Check if PDF is drug-related based on URL, link text, and surrounding context
# # #     """
# # #     # Convert to lowercase for case-insensitive matching
# # #     url_lower = url.lower()
# # #     text_lower = link_text.lower()
# # #     context_lower = context_text.lower()
    
# # #     # Drug-related keywords to look for
# # #     drug_keywords = [
# # #         'drug', 'drugs', 'pharmaceutical', 'medicine', 'medication',
# # #         'therapeutic', 'clinical', 'treatment', 'therapy', 'prescription',
# # #         'innov', 'innovative', 'registration', 'application', 'submission',
# # #         'review', 'approval', 'regulatory', 'guidance', 'guideline',
# # #         'monograph', 'label', 'safety', 'efficacy', 'trial',
# # #         'bioequivalence', 'pharmacokinetic', 'pharmacodynamic',
# # #         'dosage', 'formulation', 'indication', 'contraindication'
# # #     ]
    
# # #     # Check if any drug keywords are present
# # #     combined_text = f"{url_lower} {text_lower} {context_lower}"
    
# # #     for keyword in drug_keywords:
# # #         if keyword in combined_text:
# # #             return True
    
# # #     # Additional check for specific file patterns
# # #     drug_patterns = [
# # #         r'reg.*innov.*dr',  # reg-innov-dr pattern
# # #         r'drug.*reg',       # drug registration
# # #         r'pharma.*guid',    # pharmaceutical guidance
# # #         r'med.*applic',     # medical application
# # #         r'clinical.*guid',  # clinical guidance
# # #     ]
    
# # #     for pattern in drug_patterns:
# # #         if re.search(pattern, combined_text):
# # #             return True
    
# # #     return False

# # # def get_context_text(element):
# # #     """Get surrounding text context for better filtering"""
# # #     context = ""
    
# # #     # Get parent element text
# # #     parent = element.parent if element.parent else None
# # #     if parent:
# # #         context += parent.get_text()[:200]  # First 200 chars
    
# # #     # Get preceding sibling text
# # #     prev_sibling = element.previous_sibling
# # #     if prev_sibling and hasattr(prev_sibling, 'get_text'):
# # #         context += prev_sibling.get_text()[:100]
    
# # #     # Get following sibling text
# # #     next_sibling = element.next_sibling
# # #     if next_sibling and hasattr(next_sibling, 'get_text'):
# # #         context += next_sibling.get_text()[:100]
    
# # #     return context

# # # def convert_with_tabula(pdf_path, excel_path):
# # #     """Convert PDF to Excel using tabula-py (best for tables)"""
# # #     try:
# # #         print("📊 Using Tabula for table extraction...")
        
# # #         # Extract all tables from all pages
# # #         tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
# # #         if not tables:
# # #             print("⚠️ No tables found with Tabula")
# # #             return False
        
# # #         print(f"✅ Found {len(tables)} table(s) with Tabula")
        
# # #         # Save to Excel with multiple sheets if multiple tables
# # #         with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
# # #             for i, table in enumerate(tables):
# # #                 if not table.empty:
# # #                     sheet_name = f'Table_{i+1}' if len(tables) > 1 else 'Data'
# # #                     table.to_excel(writer, sheet_name=sheet_name, index=False)
# # #                     print(f"📋 Saved table {i+1}: {table.shape[0]} rows, {table.shape[1]} columns")
        
# # #         return True
        
# # #     except Exception as e:
# # #         print(f"❌ Tabula conversion failed: {e}")
# # #         return False

# # # def convert_with_pdfplumber(pdf_path, excel_path):
# # #     """Convert PDF to Excel using pdfplumber"""
# # #     try:
# # #         print("📄 Using PDFplumber for extraction...")
        
# # #         all_data = []
        
# # #         with pdfplumber.open(pdf_path) as pdf:
# # #             for page_num, page in enumerate(pdf.pages):
# # #                 print(f"📖 Processing page {page_num + 1}/{len(pdf.pages)}")
                
# # #                 # Try to extract tables first
# # #                 tables = page.extract_tables()
# # #                 if tables:
# # #                     for table in tables:
# # #                         # Filter out empty rows and clean data
# # #                         for row in table:
# # #                             if row and any(cell for cell in row if cell and str(cell).strip()):
# # #                                 clean_row = [str(cell).strip() if cell else "" for cell in row]
# # #                                 all_data.append(clean_row)
# # #                 else:
# # #                     # If no tables, try text extraction with structure
# # #                     text = page.extract_text()
# # #                     if text:
# # #                         lines = text.split('\n')
# # #                         for line in lines:
# # #                             line = line.strip()
# # #                             if line and not line.lower().startswith(('page ', 'confidential')):
# # #                                 # Try to detect columns by multiple spaces
# # #                                 cells = re.split(r'\s{2,}', line)
# # #                                 cells = [cell.strip() for cell in cells if cell.strip()]
# # #                                 if len(cells) > 1:  # Multi-column data
# # #                                     all_data.append(cells)
        
# # #         if all_data:
# # #             # Create DataFrame and save
# # #             max_cols = max(len(row) for row in all_data)
# # #             padded_data = [row + [''] * (max_cols - len(row)) for row in all_data]
            
# # #             df = pd.DataFrame(padded_data)
# # #             df.to_excel(excel_path, index=False, header=False)
# # #             print(f"✅ PDFplumber extracted {len(all_data)} rows")
# # #             return True
# # #         else:
# # #             print("⚠️ No data extracted with PDFplumber")
# # #             return False
            
# # #     except Exception as e:
# # #         print(f"❌ PDFplumber conversion failed: {e}")
# # #         return False

# # # def convert_with_camelot(pdf_path, excel_path):
# # #     """Convert PDF to Excel using camelot (table specialist)"""
# # #     try:
# # #         print("🐪 Using Camelot for table extraction...")
        
# # #         # Extract tables from all pages
# # #         tables = camelot.read_pdf(pdf_path, pages='all')
        
# # #         if len(tables) == 0:
# # #             print("⚠️ No tables found with Camelot")
# # #             return False
        
# # #         print(f"✅ Found {len(tables)} table(s) with Camelot")
        
# # #         # Save to Excel
# # #         with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
# # #             for i, table in enumerate(tables):
# # #                 if not table.df.empty:
# # #                     sheet_name = f'Table_{i+1}' if len(tables) > 1 else 'Data'
# # #                     table.df.to_excel(writer, sheet_name=sheet_name, index=False)
# # #                     print(f"📋 Saved table {i+1}: {table.df.shape[0]} rows, {table.df.shape[1]} columns")
# # #                     print(f"   Accuracy: {table.accuracy:.1f}%")
        
# # #         return True
        
# # #     except Exception as e:
# # #         print(f"❌ Camelot conversion failed: {e}")
# # #         return False

# # # def convert_with_pymupdf(pdf_path, excel_path):
# # #     """Convert PDF to Excel using PyMuPDF (fallback)"""
# # #     try:
# # #         print("📜 Using PyMuPDF for extraction...")
        
# # #         doc = fitz.open(pdf_path)
# # #         all_data = []
        
# # #         for page_num in range(len(doc)):
# # #             page = doc.load_page(page_num)
            
# # #             # Try table detection first
# # #             try:
# # #                 tables = page.find_tables()
# # #                 if tables:
# # #                     for table in tables:
# # #                         table_data = table.extract()
# # #                         for row in table_data:
# # #                             if row and any(cell for cell in row if cell):
# # #                                 clean_row = [str(cell).strip() if cell else "" for cell in row]
# # #                                 all_data.append(clean_row)
# # #                     continue
# # #             except:
# # #                 pass
            
# # #             # Fallback to text extraction
# # #             text = page.get_text()
# # #             if text:
# # #                 lines = text.split('\n')
# # #                 for line in lines:
# # #                     line = line.strip()
# # #                     if line and not line.lower().startswith(('page ', 'confidential')):
# # #                         cells = re.split(r'\s{2,}', line)
# # #                         cells = [cell.strip() for cell in cells if cell.strip()]
# # #                         if len(cells) > 1:
# # #                             all_data.append(cells)
        
# # #         doc.close()
        
# # #         if all_data:
# # #             max_cols = max(len(row) for row in all_data)
# # #             padded_data = [row + [''] * (max_cols - len(row)) for row in all_data]
            
# # #             df = pd.DataFrame(padded_data)
# # #             df.to_excel(excel_path, index=False, header=False)
# # #             print(f"✅ PyMuPDF extracted {len(all_data)} rows")
# # #             return True
# # #         else:
# # #             print("⚠️ No data extracted with PyMuPDF")
# # #             return False
            
# # #     except Exception as e:
# # #         print(f"❌ PyMuPDF conversion failed: {e}")
# # #         return False

# # # def convert_pdf_to_excel(pdf_path, excel_path):
# # #     """Try multiple conversion methods in order of preference"""
    
# # #     # Order of preference: tabula > camelot > pdfplumber > pymupdf
# # #     conversion_functions = {
# # #         'tabula': convert_with_tabula,
# # #         'camelot': convert_with_camelot,
# # #         'pdfplumber': convert_with_pdfplumber,
# # #         'pymupdf': convert_with_pymupdf
# # #     }
    
# # #     for method in ['tabula', 'camelot', 'pdfplumber', 'pymupdf']:
# # #         if method in conversion_methods:
# # #             print(f"\n🔄 Trying {method}...")
# # #             if conversion_functions[method](pdf_path, excel_path):
# # #                 print(f"✅ Successfully converted with {method}")
# # #                 return True
# # #             else:
# # #                 print(f"❌ {method} failed, trying next method...")
    
# # #     return False

# # # def log_failure(pdf_path, error_type, error_msg=""):
# # #     """Log failed PDF processing"""
# # #     with open("failed_innovative_drugs_pdfs.txt", "a", encoding='utf-8') as log_file:
# # #         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# # #         log_file.write(f"[{timestamp}] {error_type}: {pdf_path}")
# # #         if error_msg:
# # #             log_file.write(f" - {error_msg}")
# # #         log_file.write("\n")

# # # # --- STEP 1: Scrape PDF links ---
# # # print("🔍 Scraping drug-related PDF links from Health Canada innovative drugs page...")
# # # try:
# # #     response = requests.get(URL, timeout=30)
# # #     response.raise_for_status()
# # # except requests.RequestException as e:
# # #     print(f"❌ Failed to access website: {e}")
# # #     exit(1)

# # # soup = BeautifulSoup(response.text, "html.parser")
# # # pdf_links = []
# # # all_pdf_links = []

# # # # Find all PDF links first
# # # for a in soup.find_all("a", href=True):
# # #     href = a["href"]
# # #     if href.lower().endswith(".pdf"):
# # #         full_url = href if href.startswith("http") else f"https://www.canada.ca{href}"
# # #         link_text = a.get_text(strip=True) or "document"
# # #         context_text = get_context_text(a)
        
# # #         all_pdf_links.append({
# # #             "url": full_url,
# # #             "text": link_text,
# # #             "context": context_text
# # #         })

# # # print(f"🔍 Found {len(all_pdf_links)} total PDF files.")

# # # # Filter for drug-related PDFs
# # # for pdf_info in all_pdf_links:
# # #     if is_drug_related_pdf(pdf_info["url"], pdf_info["text"], pdf_info["context"]):
# # #         label = clean_filename(pdf_info["text"])
# # #         pdf_links.append({
# # #             "url": pdf_info["url"],
# # #             "label": label,
# # #             "original_text": pdf_info["text"]
# # #         })
# # #         print(f"✅ Drug-related PDF found: {pdf_info['text']}")
# # #         print(f"   URL: {pdf_info['url']}")
# # #     else:
# # #         print(f"⏭️ Skipped non-drug PDF: {pdf_info['text']}")

# # # print(f"\n🎯 Filtered to {len(pdf_links)} drug-related PDF files.")

# # # if not pdf_links:
# # #     print("⚠️ No drug-related PDF links found.")
# # #     print("📋 All found PDFs:")
# # #     for pdf_info in all_pdf_links:
# # #         print(f"   - {pdf_info['text']}: {pdf_info['url']}")
# # #     exit(1)

# # # # --- STEP 2: Download and Convert PDFs ---
# # # successful_count = 0
# # # failed_count = 0

# # # for i, item in enumerate(pdf_links, 1):
# # #     url = item["url"]
# # #     label = item["label"]
# # #     original_text = item["original_text"]
# # #     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# # #     pdf_path = os.path.join(SAVE_DIR, f"{label}_{timestamp}.pdf")
# # #     excel_path = os.path.join(SAVE_DIR, f"{label}_{timestamp}.xlsx")

# # #     print(f"\n📄 Processing {i}/{len(pdf_links)}: {original_text}")
# # #     print(f"=" * 60)

# # #     # ---- DOWNLOAD ----
# # #     try:
# # #         print(f"⬇️ Downloading: {url}")
# # #         r = requests.get(url, timeout=30)
# # #         r.raise_for_status()
        
# # #         with open(pdf_path, 'wb') as f:
# # #             f.write(r.content)
# # #         print(f"✅ Downloaded: {os.path.basename(pdf_path)} ({len(r.content):,} bytes)")
        
# # #     except requests.exceptions.Timeout:
# # #         print(f"⏰ Download timeout: {url}")
# # #         log_failure(pdf_path, "DownloadTimeout")
# # #         failed_count += 1
# # #         continue
# # #     except requests.exceptions.RequestException as e:
# # #         print(f"❌ Download failed: {e}")
# # #         log_failure(pdf_path, "DownloadError", str(e))
# # #         failed_count += 1
# # #         continue

# # #     # ---- CONVERT TO EXCEL ----
# # #     if convert_pdf_to_excel(pdf_path, excel_path):
# # #         print(f"📁 Excel saved: {os.path.basename(excel_path)}")
# # #         successful_count += 1
# # #     else:
# # #         print(f"❌ All conversion methods failed")
# # #         log_failure(pdf_path, "ConversionFailed")
# # #         failed_count += 1

# # #     # Optional: Remove PDF after conversion to save space
# # #     # os.remove(pdf_path)

# # #     time.sleep(1)  # Be polite to the server

# # # # --- SUMMARY ---
# # # print(f"\n" + "=" * 60)
# # # print(f"🎉 PROCESSING COMPLETE!")
# # # print(f"✅ Successfully processed: {successful_count}")
# # # print(f"❌ Failed: {failed_count}")
# # # print(f"📂 Files saved to: {os.path.abspath(SAVE_DIR)}")

# # # if failed_count > 0:
# # #     print(f"📋 Check 'failed_innovative_drugs_pdfs.txt' for details on failed files")

# # # # Installation recommendations
# # # print(f"\n💡 RECOMMENDATIONS:")
# # # if 'tabula' not in conversion_methods:
# # #     print("   pip install tabula-py              # Best for table extraction")
# # # if 'camelot' not in conversion_methods:
# # #     print("   pip install camelot-py[cv]         # Specialized table extraction")
# # # if 'pdfplumber' not in conversion_methods:
# # #     print("   pip install pdfplumber             # Good general extraction")

# # # print(f"\n📊 Available methods: {', '.join(conversion_methods)}")
# # # print(f"🎯 Target URL: {URL}")





# # import os
# # import re
# # import time
# # import requests
# # from bs4 import BeautifulSoup
# # from datetime import datetime
# # import pandas as pd

# # # Check available PDF conversion libraries
# # methods = []
# # try: import tabula; methods.append("tabula")
# # except: pass
# # try: import pdfplumber; methods.append("pdfplumber") 
# # except: pass
# # try: import camelot; methods.append("camelot")
# # except: pass
# # try: import fitz; methods.append("pymupdf")
# # except: pass

# # if not methods:
# #     print("❌ Install: pip install tabula-py pdfplumber camelot-py[cv] pymupdf")
# #     exit(1)

# # # CONFIG
# # URL = "https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/applications-submissions/register-innovative-drugs.html"
# # SAVE_DIR = "innovative_drugs"
# # os.makedirs(SAVE_DIR, exist_ok=True)

# # def clean_name(text):
# #     return re.sub(r'[^\w]', '_', text.strip().lower())[:50]

# # def is_drug_pdf(url, text):
# #     keywords = ['drug', 'innov', 'reg', 'pharma', 'clinic', 'therap', 'medic', 'guid']
# #     content = f"{url} {text}".lower()
# #     return any(k in content for k in keywords)

# # def convert_pdf(pdf_path, excel_path):
# #     # Try tabula first (best for tables)
# #     if "tabula" in methods:
# #         try:
# #             tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
# #             if tables:
# #                 with pd.ExcelWriter(excel_path) as writer:
# #                     for i, table in enumerate(tables):
# #                         if not table.empty:
# #                             table.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
# #                 print(f"✅ Tabula: {len(tables)} tables")
# #                 return True
# #         except: pass
    
# #     # Try pdfplumber
# #     if "pdfplumber" in methods:
# #         try:
# #             data = []
# #             with pdfplumber.open(pdf_path) as pdf:
# #                 for page in pdf.pages:
# #                     tables = page.extract_tables()
# #                     if tables:
# #                         for table in tables:
# #                             data.extend([row for row in table if row and any(cell for cell in row if cell)])
# #             if data:
# #                 pd.DataFrame(data).to_excel(excel_path, index=False, header=False)
# #                 print(f"✅ PDFplumber: {len(data)} rows")
# #                 return True
# #         except: pass
    
# #     # Try camelot
# #     if "camelot" in methods:
# #         try:
# #             tables = camelot.read_pdf(pdf_path, pages='all')
# #             if tables:
# #                 with pd.ExcelWriter(excel_path) as writer:
# #                     for i, table in enumerate(tables):
# #                         table.df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
# #                 print(f"✅ Camelot: {len(tables)} tables")
# #                 return True
# #         except: pass
    
# #     print("❌ All methods failed")
# #     return False

# # # Scrape PDFs
# # print("🔍 Scraping drug PDFs...")
# # response = requests.get(URL, timeout=30)
# # soup = BeautifulSoup(response.text, "html.parser")

# # pdf_links = []
# # for a in soup.find_all("a", href=True):
# #     if a["href"].lower().endswith(".pdf"):
# #         url = a["href"] if a["href"].startswith("http") else f"https://www.canada.ca{a['href']}"
# #         text = a.get_text(strip=True) or "document"
# #         if is_drug_pdf(url, text):
# #             pdf_links.append({"url": url, "name": clean_name(text)})

# # print(f"🎯 Found {len(pdf_links)} drug PDFs")

# # # Download and convert
# # success = fail = 0
# # for i, item in enumerate(pdf_links, 1):
# #     print(f"\n📄 {i}/{len(pdf_links)}: {item['name']}")
    
# #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #     pdf_path = f"{SAVE_DIR}/{item['name']}_{timestamp}.pdf"
# #     excel_path = f"{SAVE_DIR}/{item['name']}_{timestamp}.xlsx"
    
# #     # Download
# #     try:
# #         r = requests.get(item['url'], timeout=30)
# #         r.raise_for_status()
# #         with open(pdf_path, 'wb') as f:
# #             f.write(r.content)
# #         print(f"⬇️ Downloaded ({len(r.content):,} bytes)")
# #     except Exception as e:
# #         print(f"❌ Download failed: {e}")
# #         fail += 1
# #         continue
    
# #     # Convert
# #     if convert_pdf(pdf_path, excel_path):
# #         success += 1
# #     else:
# #         fail += 1
    
# #     time.sleep(1)

# # print(f"\n🎉 Done! ✅{success} ❌{fail} | Files in: {os.path.abspath(SAVE_DIR)}")
# # print(f"💡 Methods: {', '.join(methods)}")



# # method3

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

# Check available PDF conversion libraries
methods = []
try: import tabula; methods.append("tabula")
except: pass
try: import pdfplumber; methods.append("pdfplumber") 
except: pass
try: import camelot; methods.append("camelot")
except: pass
try: import fitz; methods.append("pymupdf")
except: pass

if not methods:
    print("❌ Install: pip install tabula-py pdfplumber camelot-py[cv] pymupdf")
    exit(1)

# CONFIG
URL = "https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/applications-submissions/register-innovative-drugs.html"
SAVE_DIR = "innovative_drugs"
os.makedirs(SAVE_DIR, exist_ok=True)

def clean_name(text):
    return re.sub(r'[^\w]', '_', text.strip().lower())[:50]

def is_drug_pdf(url, text):
    keywords = ['drug', 'innov', 'reg', 'pharma', 'clinic', 'therap', 'medic', 'guid']
    content = f"{url} {text}".lower()
    return any(k in content for k in keywords)

def merge_tables_smart(tables):
    """Merge multiple tables into one, handling duplicate headers intelligently"""
    if not tables:
        return pd.DataFrame()
    
    all_data = []
    common_header = None
    
    for table in tables:
        if table.empty:
            continue
            
        # Convert to list of lists for easier processing
        table_data = table.values.tolist()
        
        # Check if first row looks like headers
        if table_data and all(isinstance(cell, str) and cell.strip() for cell in table_data[0] if pd.notna(cell)):
            potential_header = [str(cell).strip() for cell in table_data[0]]
            
            # Set common header from first table
            if common_header is None:
                common_header = potential_header
                all_data.append(potential_header)  # Add header once
            
            # Skip header row if it matches common header
            if potential_header == common_header:
                all_data.extend(table_data[1:])  # Skip duplicate header
            else:
                all_data.extend(table_data)  # Different header, keep all data
        else:
            all_data.extend(table_data)  # No header detected, add all data
    
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

def convert_pdf(pdf_path, excel_path):
    # Try tabula first (best for tables)
    if "tabula" in methods:
        try:
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            if tables:
                merged_df = merge_tables_smart(tables)
                if not merged_df.empty:
                    merged_df.to_excel(excel_path, index=False, header=False)
                    print(f"✅ Tabula: {len(tables)} tables → {len(merged_df)} rows")
                    return True
        except: pass
    
    # Try pdfplumber
    if "pdfplumber" in methods:
        try:
            all_data = []
            common_header = None
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            clean_table = [row for row in table if row and any(cell for cell in row if cell)]
                            if clean_table:
                                # Check for header row
                                if clean_table[0] and all(isinstance(cell, str) for cell in clean_table[0] if cell):
                                    potential_header = [str(cell).strip() for cell in clean_table[0]]
                                    
                                    if common_header is None:
                                        common_header = potential_header
                                        all_data.extend(clean_table)
                                    elif potential_header == common_header:
                                        all_data.extend(clean_table[1:])  # Skip duplicate header
                                    else:
                                        all_data.extend(clean_table)
                                else:
                                    all_data.extend(clean_table)
            
            if all_data:
                pd.DataFrame(all_data).to_excel(excel_path, index=False, header=False)
                print(f"✅ PDFplumber: {len(all_data)} rows")
                return True
        except: pass
    
    # Try camelot
    if "camelot" in methods:
        try:
            tables = camelot.read_pdf(pdf_path, pages='all')
            if tables:
                table_dfs = [table.df for table in tables if not table.df.empty]
                merged_df = merge_tables_smart(table_dfs)
                if not merged_df.empty:
                    merged_df.to_excel(excel_path, index=False, header=False)
                    print(f"✅ Camelot: {len(tables)} tables → {len(merged_df)} rows")
                    return True
        except: pass
    
    print("❌ All methods failed")
    return False

# Scrape PDFs
print("🔍 Scraping drug PDFs...")
response = requests.get(URL, timeout=30)
soup = BeautifulSoup(response.text, "html.parser")

pdf_links = []
for a in soup.find_all("a", href=True):
    if a["href"].lower().endswith(".pdf"):
        url = a["href"] if a["href"].startswith("http") else f"https://www.canada.ca{a['href']}"
        text = a.get_text(strip=True) or "document"
        if is_drug_pdf(url, text):
            pdf_links.append({"url": url, "name": clean_name(text)})

print(f"🎯 Found {len(pdf_links)} drug PDFs")

# Download and convert
success = fail = 0
for i, item in enumerate(pdf_links, 1):
    print(f"\n📄 {i}/{len(pdf_links)}: {item['name']}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"{SAVE_DIR}/{item['name']}_{timestamp}.pdf"
    excel_path = f"{SAVE_DIR}/{item['name']}_{timestamp}.xlsx"
    
    # Download
    try:
        r = requests.get(item['url'], timeout=30)
        r.raise_for_status()
        with open(pdf_path, 'wb') as f:
            f.write(r.content)
        print(f"⬇️ Downloaded ({len(r.content):,} bytes)")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        fail += 1
        continue
    
    # Convert
    if convert_pdf(pdf_path, excel_path):
        success += 1
    else:
        fail += 1
    
    time.sleep(1)

print(f"\n🎉 Done! ✅{success} ❌{fail} | Files in: {os.path.abspath(SAVE_DIR)}")
print(f"💡 Methods: {', '.join(methods)}")

# Method 4

# import os, re, requests, time, pandas as pd
# from bs4 import BeautifulSoup
# from datetime import datetime

# # Check PDF libraries
# methods = []
# try: import tabula; methods.append("tabula")
# except: pass
# try: import pdfplumber; methods.append("pdfplumber")
# except: pass
# try: import camelot; methods.append("camelot")
# except: pass

# if not methods:
#     print("❌ Install: pip install tabula-py pdfplumber camelot-py[cv]")
#     exit(1)

# # Config
# URL = "https://www.canada.ca/en/health-canada/services/drugs-health-products/drug-products/applications-submissions/register-innovative-drugs.html"
# SAVE_DIR = "drugs"
# os.makedirs(SAVE_DIR, exist_ok=True)

# def merge_smart(tables):
#     data, header = [], None
#     for t in tables:
#         if t.empty: continue
#         rows = t.values.tolist()
#         if rows and all(isinstance(c, str) for c in rows[0] if pd.notna(c)):
#             h = [str(c).strip() for c in rows[0]]
#             if header is None: header, data = h, [h]
#             data.extend(rows[1:] if h == header else rows)
#         else: data.extend(rows)
#     return pd.DataFrame(data)

# def convert_pdf(pdf_path, excel_path):
#     # Tabula
#     if "tabula" in methods:
#         try:
#             tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
#             if tables:
#                 df = merge_smart(tables)
#                 df.to_excel(excel_path, index=False, header=False)
#                 print(f"✅ {len(tables)} tables → {len(df)} rows")
#                 return True
#         except: pass
    
#     # PDFplumber
#     if "pdfplumber" in methods:
#         try:
#             data, header = [], None
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     for table in page.extract_tables() or []:
#                         clean = [r for r in table if r and any(c for c in r if c)]
#                         if clean:
#                             if clean[0] and all(isinstance(c, str) for c in clean[0] if c):
#                                 h = [str(c).strip() for c in clean[0]]
#                                 if header is None: header, data = h, clean
#                                 else: data.extend(clean[1:] if h == header else clean)
#                             else: data.extend(clean)
#             if data:
#                 pd.DataFrame(data).to_excel(excel_path, index=False, header=False)
#                 print(f"✅ {len(data)} rows")
#                 return True
#         except: pass
    
#     # Camelot
#     if "camelot" in methods:
#         try:
#             tables = camelot.read_pdf(pdf_path, pages='all')
#             if tables:
#                 df = merge_smart([t.df for t in tables])
#                 df.to_excel(excel_path, index=False, header=False)
#                 print(f"✅ {len(tables)} tables → {len(df)} rows")
#                 return True
#         except: pass
    
#     return False

# # Scrape
# response = requests.get(URL)
# soup = BeautifulSoup(response.text, "html.parser")

# pdfs = []
# for a in soup.find_all("a", href=True):
#     if a["href"].lower().endswith(".pdf"):
#         url = a["href"] if a["href"].startswith("http") else f"https://www.canada.ca{a['href']}"
#         text = a.get_text(strip=True) or "doc"
#         if any(k in f"{url} {text}".lower() for k in ['drug', 'innov', 'reg', 'pharma', 'clinic']):
#             pdfs.append({"url": url, "name": re.sub(r'[^\w]', '_', text.lower())[:30]})

# print(f"🎯 {len(pdfs)} drug PDFs found")

# # Process
# success = 0
# for i, pdf in enumerate(pdfs, 1):
#     print(f"\n📄 {i}/{len(pdfs)}: {pdf['name']}")
#     ts = datetime.now().strftime("%m%d_%H%M")
#     pdf_path = f"{SAVE_DIR}/{pdf['name']}_{ts}.pdf"
#     excel_path = f"{SAVE_DIR}/{pdf['name']}_{ts}.xlsx"
    
#     try:
#         r = requests.get(pdf['url'], timeout=30)
#         with open(pdf_path, 'wb') as f: f.write(r.content)
#         print(f"⬇️ {len(r.content):,} bytes")
        
#         if convert_pdf(pdf_path, excel_path): success += 1
#         else: print("❌ Convert failed")
#         time.sleep(1)
#     except Exception as e:
#         print(f"❌ {e}")

# print(f"\n🎉 Done! ✅{success}/{len(pdfs)} | {os.path.abspath(SAVE_DIR)}")