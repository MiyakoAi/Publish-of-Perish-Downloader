import os
import hashlib

def hash_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_files(folder_path):
    hash_map = {}
    duplicates = []

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                file_hash = hash_file(filepath)
                if file_hash in hash_map:
                    duplicates.append((filepath, hash_map[file_hash]))
                else:
                    hash_map[file_hash] = filepath
            except Exception as e:
                print(f"❌ Gagal memproses: {filepath} karena {e}")

    return duplicates

folder = r"pdf_jurnal" #folder
duplikat = find_duplicate_files(folder)

if duplikat:
    print("\n📄 File Duplikat Ditemukan:")
    for dup in duplikat:
        print(f"🟢 {dup[0]}\n    ↔️ {dup[1]}\n")
else:
    print("✅ Tidak ditemukan file duplikat.")
