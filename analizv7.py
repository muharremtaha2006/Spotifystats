import json
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import defaultdict
from PIL import Image, ImageTk

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_data(data):
    song_totals = defaultdict(lambda: {"artist": "Unknown", "album": "Unknown", "total_minutes": 0})

    for entry in data:
        track_name = entry.get("master_metadata_track_name", "Unknown")
        artist_name = entry.get("master_metadata_album_artist_name", "Unknown")
        album_name = entry.get("master_metadata_album_album_name", "Unknown")
        minutes_played = entry.get("ms_played", 0) // 60000

        if track_name != "Unknown":
            song_totals[track_name]["artist"] = artist_name
            song_totals[track_name]["album"] = album_name
            song_totals[track_name]["total_minutes"] += minutes_played

    sorted_songs = sorted(
        [{"track_name": track, **info} for track, info in song_totals.items()],
        key=lambda x: x["total_minutes"],
        reverse=True,
    )
    return sorted_songs

def display_data(analyzed_data):
    root = tk.Tk()
    root.title("Toplam Dinleme Süreleri")
    root.geometry("1000x600")
    root.configure(bg="#2c2c2c")

    # Arka plan resmi
    bg_image_path = "background.jpg"  # Arka plan resmi
    try:
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((1000, 600), Image.ANTIALIAS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(relwidth=1, relheight=1)
    except:
        pass  # Arka plan resmi yoksa hata almayalım

    # Başlık
    title = tk.Label(root, text="Toplam Dinleme Süreleri", font=("Arial", 20, "bold"), bg="#4CAF50", fg="white", pady=10)
    title.pack(fill=tk.X)

    # Şarkılar tablosu
    frame = tk.Frame(root, bg="#2c2c2c")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Toplam Dinleme Süresi (dk)")
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Tablodaki sütun başlıkları
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#6C63FF", foreground="white")
    style.configure("Treeview", font=("Arial", 10), rowheight=25, background="#f9f9f9", foreground="#333")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=200, stretch=True)

    for item in analyzed_data:
        tree.insert(
            "", tk.END,
            values=(
                item["track_name"],
                item["artist"],
                item["album"],
                item["total_minutes"],
            ),
        )

    # Kaydırma çubuğu
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
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

        analyzed_data = analyze_data(all_data)
        display_data(analyzed_data)

def choose_file():
    file_path = filedialog.askopenfilename(title="Bir JSON dosyası seçin", filetypes=[("JSON Files", "*.json")])
    if file_path:
        try:
            data = read_json(file_path)
            analyzed_data = analyze_data(data)
            display_data(analyzed_data)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunurken hata oluştu: {e}")

def main_interface():
    root = tk.Tk()
    root.title("JSON Dinleme Verisi Analizörü")
    root.geometry("500x300")
    root.configure(bg="#2c2c2c")
    root.resizable(False, False)

    # Arka plan resmi (Opsiyonel)
    bg_image_path = "background.jpg"
    try:
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((500, 300), Image.ANTIALIAS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(relwidth=1, relheight=1)
    except:
        pass

    # Başlık
    title_label = tk.Label(root, text="JSON Dinleme Verisi Analizörü", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white")
    title_label.pack(pady=20, fill=tk.X)

    # Düğmeler
    select_dir_button = tk.Button(root, text="Klasör Seç", command=choose_directory, font=("Arial", 12), bg="#6C63FF", fg="white", pady=5)
    select_dir_button.pack(pady=10)

    select_file_button = tk.Button(root, text="Dosya Seç", command=choose_file, font=("Arial", 12), bg="#6C63FF", fg="white", pady=5)
    select_file_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        main_interface()
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
