import os
import re
import requests
from tqdm import tqdm
import json

# Folder penyimpanan file
output_dir = "pdf_jurnal"
os.makedirs(output_dir, exist_ok=True)

# Baca file JSON
try:          # Json File
    with open("test2.json", "r", encoding="utf-8-sig") as f:
        data = json.load(f)
except Exception as e:
    print(f"🚫 Gagal membaca file JSON: {e}")
    exit()

url_fields = ["fulltext_url", "fullTextUrl", "pdf_url", "article_url", "url", "download_url"]

def sanitize_filename(name: str) -> str:
    """Bersihkan nama file dari karakter ilegal."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip().replace(" ", "_")
    return name[:200]

entries = []
no_access_count = 0
invalid_entry_count = 0

for idx, item in enumerate(data):
    if not isinstance(item, dict):
        invalid_entry_count += 1
        continue

    pdf_url = None
    for field in url_fields:
        if field in item and item[field]:
            pdf_url = item[field]
            break
    if not pdf_url:
        no_access_count += 1
        continue

    title = item.get("title") or f"paper_{idx}"
    filename = sanitize_filename(title) + ".pdf"
    filepath = os.path.join(output_dir, filename)

    entries.append({
        "url": pdf_url,
        "filepath": filepath,
        "title": title
    })

if not entries:
    print("🚫 Tidak ada entri valid dengan fulltext_url/pdf_url di JSON.")
    exit()

success_count = 0
fail_count = 0
error_count = 0
skip_count = 0

for e in tqdm(entries, desc="Downloading"):
    url = e["url"]
    path = e["filepath"]
    if os.path.exists(path):
        tqdm.write(f"⏭️ Sudah ada, skip: {os.path.basename(path)}")
        skip_count += 1
        continue
    try:
        resp = requests.get(url, timeout=20)
        if resp.ok and resp.content.startswith(b"%PDF"):
            with open(path, "wb") as f:
                f.write(resp.content)
            tqdm.write(f"✅ Saved: {os.path.basename(path)}")
            success_count += 1
        else:
            tqdm.write(f"❌ Failed : {e['title']}")
            fail_count += 1
    except Exception as err:
        tqdm.write(f"⚠️ Error {e['title']}: {err}")
        error_count += 1

print("\n📥 Proses download selesai.")
print(f"📂 File disimpan di: {os.path.abspath(output_dir)}")
print("\n📊 Ringkasan Unduhan:")
print(f"✅ Berhasil            : {success_count}")
print(f"⏭️  Sudah ada           : {skip_count}")
print(f"❌ Gagal               : {fail_count}")
print(f"⚠️  Error               : {error_count}")
print(f"🔍 Tidak Ada Akses URL : {no_access_count}")
print(f"🚫 Data Rusak          : {invalid_entry_count}")
print(f"📁 Total File          : {len(entries)}")