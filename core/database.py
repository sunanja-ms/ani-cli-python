import json
import os
import time

DATA_FILE = "data.json"
SETTINGS_FILE = "config.ini"

def load_data(file_path):
    """Memuat data dari file JSON."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    return {}

def save_data(data, file_path):
    """Menyimpan data ke file JSON."""
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saat menyimpan data: {e}")
        return False

def get_settings():
    """Memuat pengaturan dari config.ini."""
    data = {}
    try:
        with open(SETTINGS_FILE, "r") as r:
            for line in r:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    data[key.strip()] = value.strip()
    except FileNotFoundError:
        # Buat file default jika tidak ada
        with open(SETTINGS_FILE, "w") as w:
            w.write("default_quality=720p\n")
            w.write("mpv_path=mpv\n")
        return {"default_quality": "720p", "mpv_path": "mpv"}
    return data

def set_setting(key, value):
    """Menyimpan satu pengaturan ke config.ini."""
    settings = get_settings()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, "w") as w:
            for k, v in settings.items():
                w.write(f"{k}={v}\n")
        return True
    except Exception as e:
        print(f"Error saat menyimpan pengaturan: {e}")
        return False

def save_bookmark(anime_info: dict):
    """Menyimpan data anime ke bookmark."""
    data = load_data(DATA_FILE)
    if 'bookmarks' not in data:
        data['bookmarks'] = {}
    
    title = anime_info.get('title')
    if not title:
        print("Judul tidak ditemukan, tidak bisa menyimpan bookmark.")
        return False
        
    # Memastikan URL utama anime tersimpan
    data['bookmarks'][title] = {
        'url': anime_info.get('url'), # Ini penting untuk membuka detail lagi
        'cover': anime_info.get('cover'),
        'info': anime_info.get('info'),
        'sinopsis': anime_info.get('sinopsis'),
        'timestamp': int(time.time())
    }
    return save_data(data, DATA_FILE)

def get_bookmarks():
    """Mengambil semua bookmark."""
    return load_data(DATA_FILE).get('bookmarks', {})

def delete_bookmark(title):
    """Menghapus bookmark berdasarkan judul."""
    data = load_data(DATA_FILE)
    if 'bookmarks' in data and title in data['bookmarks']:
        del data['bookmarks'][title]
        return save_data(data, DATA_FILE)
    return False

def save_history(anime_info: dict, episode_info: dict):
    """Menyimpan riwayat tontonan anime."""
    data = load_data(DATA_FILE)
    if 'history' not in data:
        data['history'] = {}

    anime_title = anime_info.get('title')
    if not anime_title:
        print("Judul tidak ditemukan, tidak bisa menyimpan riwayat.")
        return False

    # Menggunakan judul anime sebagai kunci utama untuk menimpa riwayat episode terakhir
    data['history'][anime_title] = {
        'anime_url': anime_info.get('url'),
        'episode_title': episode_info.get('title'),
        'episode_url': episode_info.get('url'),
        'cover': anime_info.get('cover'),
        'timestamp': int(time.time())
    }
    return save_data(data, DATA_FILE)

def get_history():
    """Mengambil semua riwayat tontonan, diurutkan dari yang terbaru."""
    history = load_data(DATA_FILE).get('history', {})
    # Mengubah dict menjadi list, mengurutkan, lalu mengubahnya kembali ke dict
    sorted_history = sorted(history.items(), key=lambda item: item[1]['timestamp'], reverse=True)
    return dict(sorted_history)



