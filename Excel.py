import requests
import os
from datetime import datetime

# ---- CONFIG ----
DOWNLOAD_URL = "https://www.canada.ca/content/dam/hc-sc/documents/services/drug-health-product-review-approval/generic-submissions-under-review/generic-submissions-under-review-2025-04.xlsx"
SAVE_DIR = "downloads"
FILENAME_PREFIX = "Canada_Generic_Submissions"

# ---- SETUP ----
os.makedirs(SAVE_DIR, exist_ok=True)
today_str = datetime.today().strftime("%Y-%m-%d")
filename = f"{FILENAME_PREFIX}_{today_str}.xlsx"
file_path = os.path.join(SAVE_DIR, filename)

# ---- DOWNLOAD ----
def download_excel():
    try:
        response = requests.get(DOWNLOAD_URL)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"[{datetime.now()}] ✅ File saved to: {file_path}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Download failed: {e}")

# ---- MAIN ----
if __name__ == "__main__":
    download_excel()