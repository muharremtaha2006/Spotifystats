import json
import os
import tkinter as tk
from tkinter import filedialog, ttk
from collections import Counter

# JSON dosyasını okuyun
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Dinleme verilerini analiz et
def analyze_data(data):
    analyzed_data = []
    artist_count = Counter()

    for entry in data:
        track_name = entry.get("master_metadata_track_name", "Unknown")
        artist_name = entry.get("master_metadata_album_artist_name", "Unknown")
        album_name = entry.get("master_metadata_album_album_name", "Unknown")
        minutes_played = entry.get("ms_played", 0) // 60000

        artist_count[artist_name] += minutes_played

        analyzed_data.append({
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "minutes_played": minutes_played
        })

    most_played_artist = artist_count.most_common(1)
    return analyzed_data, most_played_artist[0] if most_played_artist else ("Unknown", 0)

# Verileri GUI'de göster
def display_data(data, most_played_artist):
    root = tk.Tk()
    root.title("Dinleme Verileri")

    # Üstbilgi kısmı
    header = tk.Label(root, text=f"En Çok Dinlenen Sanatçı: {most_played_artist[0]} ({most_played_artist[1]} dakika)", font=("Arial", 14, "bold"))
    header.pack(pady=10)

    # Tablo oluştur
    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Dinleme Süresi (dk)")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=200, stretch=True)

    # Verileri tabloya ekle
    for item in data:
        tree.insert("", tk.END, values=(item["track_name"], item["artist_name"], item["album_name"], item["minutes_played"]))

    # Kaydırma çubuğu ekle
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    root.mainloop()

# Bir klasördeki tüm JSON dosyalarını oku
def read_all_json_in_directory(directory_path):
    all_data = []

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory_path, file_name)
            try:
                data = read_json(file_path)
                all_data.extend(data)
            except Exception as e:
                print(f"Dosya okunurken hata oluştu: {file_name}. Hata: {e}")

    return all_data

# Arayüzü başlat
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle

    # Klasör seç
    directory_path = filedialog.askdirectory(title="JSON dosyalarının bulunduğu klasörü seçin")
    if not directory_path:
        print("Klasör seçilmedi. İşlem iptal edildi.")
        exit()

    # Klasördeki tüm JSON dosyalarını yükle
    all_data = read_all_json_in_directory(directory_path)

    if not all_data:
        print("Hiçbir veri bulunamadı. İşlem iptal edildi.")
        exit()

    # Verileri analiz et
    analyzed_data, most_played_artist = analyze_data(all_data)

    # Verileri göster
    display_data(analyzed_data, most_played_artist)
