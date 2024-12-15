import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
from PIL import Image, ImageTk
import customtkinter as ctk  # Modern arayüz için

# CustomTkinter temasını ayarlama
ctk.set_appearance_mode("dark")  # "dark" veya "light"
ctk.set_default_color_theme("blue")  # Tema: "blue", "green", "dark-blue"

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
    root = ctk.CTk()
    root.title("Toplam Dinleme Süreleri")
    root.geometry("1000x600")

    # Özel başlık çubuğu
    def close_window():
        root.destroy()

    def minimize_window():
        root.iconify()

    title_bar = ctk.CTkFrame(root, height=40, fg_color="#1a1a1a")
    title_bar.pack(side="top", fill="x")
    title_label = ctk.CTkLabel(title_bar, text="Dinleme Verisi Analizörü", font=("Arial", 14, "bold"))
    title_label.place(x=10, y=5)

    close_button = ctk.CTkButton(title_bar, text="X", width=30, fg_color="red", command=close_window)
    close_button.place(x=960, y=5)
    minimize_button = ctk.CTkButton(title_bar, text="-", width=30, fg_color="#4CAF50", command=minimize_window)
    minimize_button.place(x=920, y=5)

    # Şarkılar tablosu
    frame = ctk.CTkFrame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Toplam Dinleme Süresi (dk)")
    tree = ctk.CTkScrollableFrame(frame, width=950, height=450)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    header_frame = ctk.CTkFrame(tree)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    # Tablo başlıkları
    for col in columns:
        header = ctk.CTkLabel(header_frame, text=col, font=("Arial", 12, "bold"))
        header.pack(side="left", padx=50)

    # Tablo satırları
    for item in analyzed_data:
        row_frame = ctk.CTkFrame(tree)
        row_frame.pack(fill=tk.X, pady=5)

        ctk.CTkLabel(row_frame, text=item["track_name"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=item["artist"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=item["album"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=str(item["total_minutes"]), font=("Arial", 10)).pack(side="left", padx=50)

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
    root = ctk.CTk()
    root.title("JSON Dinleme Verisi Analizörü")
    root.geometry("500x300")
    root.resizable(False, False)

    # Logo ekleme
    try:
        logo_image = Image.open("logo.png")  # Logonuzun yolunu belirtin
        logo_image = logo_image.resize((100, 100), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ctk.CTkLabel(root, image=logo_photo, text="")
        logo_label.image = logo_photo
        logo_label.pack(pady=20)
    except:
        pass

    # Başlık
    title_label = ctk.CTkLabel(root, text="JSON Dinleme Verisi Analizörü", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Düğmeler
    select_dir_button = ctk.CTkButton(root, text="Klasör Seç", command=choose_directory, font=("Arial", 12))
    select_dir_button.pack(pady=10)

    select_file_button = ctk.CTkButton(root, text="Dosya Seç", command=choose_file, font=("Arial", 12))
    select_file_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        main_interface()
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
