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
    track_count = Counter()

    for entry in data:
        track_name = entry.get("master_metadata_track_name", "Unknown")
        artist_name = entry.get("master_metadata_album_artist_name", "Unknown")
        album_name = entry.get("master_metadata_album_album_name", "Unknown")
        minutes_played = entry.get("ms_played", 0) // 60000

        track_count[track_name] += minutes_played

        analyzed_data.append({
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "minutes_played": minutes_played
        })

    analyzed_data.sort(key=lambda x: x["minutes_played"], reverse=True)
    sorted_tracks = track_count.most_common()
    return analyzed_data, sorted_tracks

def display_data(analyzed_data, sorted_tracks):
    root = tk.Tk()
    root.title("Dinleme Verileri")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Tüm Şarkılar Tablosu
    all_songs_frame = ttk.Frame(notebook)
    notebook.add(all_songs_frame, text="Tüm Şarkılar")

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Dinleme Süresi (dk)")
    tree = ttk.Treeview(all_songs_frame, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=200, stretch=True)

    for item in analyzed_data:
        tree.insert("", tk.END, values=(item["track_name"], item["artist_name"], item["album_name"], item["minutes_played"]))

    scrollbar = ttk.Scrollbar(all_songs_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Dinleme Özeti Tablosu
    summary_frame = ttk.Frame(notebook)
    notebook.add(summary_frame, text="Dinleme Özeti")

    summary_columns = ("Şarkı Adı", "Toplam Dinleme Süresi (dk)")
    summary_tree = ttk.Treeview(summary_frame, columns=summary_columns, show="headings")
    summary_tree.pack(fill=tk.BOTH, expand=True)

    for col in summary_columns:
        summary_tree.heading(col, text=col)
        summary_tree.column(col, minwidth=0, width=300, stretch=True)

    for track, minutes in sorted_tracks:
        summary_tree.insert("", tk.END, values=(track, minutes))

    summary_scrollbar = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=summary_tree.yview)
    summary_tree.configure(yscroll=summary_scrollbar.set)
    summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

        analyzed_data, sorted_tracks = analyze_data(all_data)
        display_data(analyzed_data, sorted_tracks)

def main_interface():
    root = tk.Tk()
    root.title("JSON Dinleme Verisi Analizörü")
    root.geometry("500x250")

    title_label = tk.Label(root, text="JSON Dinleme Verisi Analizörü", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    select_dir_button = tk.Button(root, text="Klasör Seç", command=choose_directory, font=("Arial", 12))
    select_dir_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main_interface()
