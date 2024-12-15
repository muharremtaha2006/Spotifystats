import json
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import Counter

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

    analyzed_data.sort(key=lambda x: x["minutes_played"], reverse=True)
    most_played_artist = artist_count.most_common(1)
    return analyzed_data, most_played_artist[0] if most_played_artist else ("Unknown", 0)

def display_data(data, most_played_artist):
    root = tk.Tk()
    root.title("Dinleme Verileri")

    header = tk.Label(root, text=f"En Çok Dinlenen Sanatçı: {most_played_artist[0]} ({most_played_artist[1]} dakika)", font=("Arial", 14, "bold"))
    header.pack(pady=10)

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Dinleme Süresi (dk)")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=200, stretch=True)

    for item in data:
        tree.insert("", tk.END, values=(item["track_name"], item["artist_name"], item["album_name"], item["minutes_played"]))

    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    root.mainloop()

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

def choose_directory():
    directory_path = filedialog.askdirectory(title="JSON dosyalarının bulunduğu klasörü seçin")
    if directory_path:
        all_data = read_all_json_in_directory(directory_path)

        if not all_data:
            messagebox.showerror("Hata", "Hiçbir veri bulunamadı.")
            return

        analyzed_data, most_played_artist = analyze_data(all_data)
        display_data(analyzed_data, most_played_artist)

def choose_file():
    file_path = filedialog.askopenfilename(title="Bir JSON dosyası seçin", filetypes=[("JSON Files", "*.json")])
    if file_path:
        try:
            data = read_json(file_path)
            analyzed_data, most_played_artist = analyze_data(data)
            display_data(analyzed_data, most_played_artist)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunurken hata oluştu: {e}")
            
def main_interface():
    root = tk.Tk()
    root.title("JSON Dinleme Verisi Analizörü")
    root.geometry("500x250")
    root.resizable(False, False)  # Pencerenin boyutunu sabitle

    title_label = tk.Label(root, text="JSON Dinleme Verisi Analizörü", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    select_dir_button = tk.Button(root, text="Klasör Seç", command=choose_directory, font=("Arial", 12))
    select_dir_button.pack(pady=10)

    select_file_button = tk.Button(root, text="Dosya Seç", command=choose_file, font=("Arial", 12))
    select_file_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        main_interface()
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
