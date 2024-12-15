import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
from PIL import Image, ImageTk
import customtkinter as ctk

# Varsayılan ayarları ve JSON yolu
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"background_type": "color", "background_value": "black"}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def apply_background(root, settings):
    """Optimize arka plan yüklemesi."""
    if settings["background_type"] == "color":
        root.configure(bg=settings["background_value"])
    elif settings["background_type"] == "image":
        try:
            img = Image.open(settings["background_value"])
            img = img.resize((root.winfo_width(), root.winfo_height()), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)
            bg_label = tk.Label(root, image=photo)
            bg_label.image = photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Arka plan yüklenirken hata: {e}")
            root.configure(bg="black")

def load_data_in_thread(directory_path, callback):
    """Arka planda veri yükler."""
    def task():
        try:
            data = []
            for filename in os.listdir(directory_path):
                if filename.endswith(".json"):
                    with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as f:
                        data.extend(json.load(f))
            callback(data)
        except Exception as e:
            messagebox.showerror("Hata", f"Veriler yüklenemedi: {e}")
    threading.Thread(target=task).start()

def analyze_data(data):
    """Dinlenen müzikleri analiz eder."""
    analyzed_data = defaultdict(int)
    for entry in data:
        track_name = entry.get("master_metadata_track_name", "Unknown")
        minutes_played = entry.get("ms_played", 0) // 60000
        analyzed_data[track_name] += minutes_played

    sorted_data = sorted(analyzed_data.items(), key=lambda x: x[1], reverse=True)
    return [{"track_name": k, "total_minutes": v} for k, v in sorted_data]

def display_data(data):
    """Verileri ekranda görüntüler."""
    root = ctk.CTk()
    root.title("Dinleme Analizleri")
    root.geometry("800x600")
    root.resizable(False, False)

    settings = load_settings()
    apply_background(root, settings)

    # Modern başlık
    title_bar = ctk.CTkFrame(root, height=40)
    title_bar.pack(side="top", fill="x")
    title_label = ctk.CTkLabel(title_bar, text="Dinleme Verisi Analizörü", font=("Arial", 14))
    title_label.place(x=10, y=5)

    # Çıkış düğmesi
    def close_window():
        root.destroy()
    close_button = ctk.CTkButton(title_bar, text="X", command=close_window, width=30, fg_color="red")
    close_button.place(x=750, y=5)

    # Tablo çerçevesi
    table_frame = ctk.CTkFrame(root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Tablo başlıkları
    header = ctk.CTkLabel(table_frame, text="Şarkı Adı ve Dinleme Süreleri", font=("Arial", 12, "bold"))
    header.pack(pady=10)

    # Tablonun kendisi
    columns = ("Şarkı Adı", "Toplam Süre (dk)")
    tree = ctk.CTkScrollableFrame(table_frame, width=760, height=500)
    tree.pack(padx=10, pady=10)

    for col in columns:
        header_label = ctk.CTkLabel(tree, text=col, font=("Arial", 10, "bold"))
        header_label.pack(pady=5)

    # Satır ekleme
    def populate_table():
        for item in data:
            row = f"{item['track_name']} - {item['total_minutes']} dk"
            row_label = ctk.CTkLabel(tree, text=row, font=("Arial", 10))
            row_label.pack(pady=5)

    threading.Thread(target=populate_table).start()

    root.mainloop()

def choose_directory_and_load():
    """Klasör seçer ve verileri yükler."""
    directory = filedialog.askdirectory(title="JSON Dosyalarını Seç")
    if not directory:
        return
    load_data_in_thread(directory, lambda data: display_data(analyze_data(data)))

def main_interface():
    """Ana arayüz."""
    root = ctk.CTk()
    root.title("JSON Dinleme Verisi Analizörü")
    root.geometry("500x300")
    root.resizable(False, False)

    # Modern başlık
    title_label = ctk.CTkLabel(root, text="Dinleme Verisi Analizörü", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    # Klasör seç düğmesi
    select_dir_btn = ctk.CTkButton(root, text="Klasör Seç", command=choose_directory_and_load)
    select_dir_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_interface()
