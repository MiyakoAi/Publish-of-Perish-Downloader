import os
import re
import requests
from tqdm import tqdm
import json

# Folder penyimpanan file PDF
output_dir = "pdf_jurnal" # nama folder
os.makedirs(output_dir, exist_ok=True)

# Baca file JSON, folder di sini "test4.json" ganti dengan nama file JSON yang lain
with open("test2.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

url_fields = ["fulltext_url", "fullTextUrl", "pdf_url", "article_url", "url", "download_url"] # Tambahkan object lain jika ada di file JSON

def sanitize_filename(name: str) -> str:
    """Bersihkan nama file dari karakter ilegal."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip().replace(" ", "_")
    return name[:200]  # batasi panjang nama

entries = []
for idx, item in enumerate(data):

    pdf_url = None
    for field in url_fields:
        if field in item and item[field]:
            pdf_url = item[field]
            break
    if not pdf_url:
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
    print("🚫 Tidak ada entri dengan fulltext_url/pdf_url di JSON. Cek nama field Json-nya.")
    exit()

for e in tqdm(entries, desc="Downloading"):
    url = e["url"]
    path = e["filepath"]
    if os.path.exists(path):
        tqdm.write(f"⏭️ Sudah ada, skip: {os.path.basename(path)}")
        continue
    try:
        resp = requests.get(url, timeout=20)
        if resp.ok and resp.content.startswith(b"%PDF"):
            with open(path, "wb") as f:
                f.write(resp.content)
            tqdm.write(f"✅ Saved: {os.path.basename(path)}")
        else:
            tqdm.write(f"❌ Bukan PDF atau gagal untuk: {e['title']}")
    except Exception as err:
        tqdm.write(f"⚠️ Error untuk {e['title']}: {err}")
print()
print("📥 Proses download selesai.")
print(f"📂 File disimpan di: {os.path.abspath(output_dir)}") 