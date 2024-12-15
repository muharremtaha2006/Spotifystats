import json
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import defaultdict
from PIL import Image, ImageTk
import customtkinter as ctk

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"background_type": "color", "background_value": "black", "theme": "dark"}
LOGO_PATH = "logo.png"  # Sol üst köşe için logo dosyası


# Ayarlar Yükleme ve Kaydetme
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETTINGS


def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)


# Arka Plan ve Tema Uygulama
def apply_theme_and_background(root, settings):
    for widget in root.winfo_children():
        widget.destroy()

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
            messagebox.showerror("Hata", f"Arka plan yüklenirken hata oluştu: {e}")
            root.configure(bg="black")

    ctk.set_appearance_mode(settings.get("theme", "dark"))


# Veri Yükleme ve Analiz
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_data(data):
    analyzed_data = defaultdict(lambda: {"minutes_played": 0, "artist_name": "", "album_name": ""})
    for entry in data:
        track_name = entry.get("master_metadata_track_name", "Unknown")
        artist_name = entry.get("master_metadata_album_artist_name", "Unknown")
        album_name = entry.get("master_metadata_album_album_name", "Unknown")
        minutes_played = entry.get("ms_played", 0) // 60000

        analyzed_data[track_name]["minutes_played"] += minutes_played
        analyzed_data[track_name]["artist_name"] = artist_name
        analyzed_data[track_name]["album_name"] = album_name

    sorted_data = sorted(analyzed_data.items(), key=lambda x: x[1]["minutes_played"], reverse=True)
    return [{"track_name": k, **v} for k, v in sorted_data]


# Verileri Tabloya Gösterme
def display_data(data, root, settings):
    apply_theme_and_background(root, settings)

    title_bar = ctk.CTkFrame(root, height=50, corner_radius=10)
    title_bar.pack(side="top", fill="x", padx=10, pady=10)

    # Logo ekleme
    if os.path.exists(LOGO_PATH):
        logo_img = Image.open(LOGO_PATH).resize((40, 40), Image.ANTIALIAS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(title_bar, image=logo_photo, bg="black")
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=10)

    title_label = ctk.CTkLabel(title_bar, text="Dinleme Verisi Analizörü", font=("Arial", 18, "bold"))
    title_label.pack(side="left", pady=5)

    table_frame = ctk.CTkFrame(root, corner_radius=10)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Dinleme Süresi (dk)")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.W)

    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for item in data:
        tree.insert("", tk.END, values=(item["track_name"], item["artist_name"], item["album_name"], item["minutes_played"]))


# Klasör Seçme
def choose_directory(root, settings):
    directory_path = filedialog.askdirectory(title="JSON Dosyalarının Bulunduğu Klasörü Seçin")
    if not directory_path:
        return

    all_data = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".json"):
            try:
                file_path = os.path.join(directory_path, file_name)
                all_data.extend(read_json(file_path))
            except Exception as e:
                print(f"Dosya okunurken hata oluştu: {file_name}. Hata: {e}")

    if all_data:
        analyzed_data = analyze_data(all_data)
        display_data(analyzed_data, root, settings)
    else:
        messagebox.showerror("Hata", "Hiçbir veri bulunamadı.")


# Ayarlar Arayüzü
def settings_menu(root):
    settings = load_settings()
    apply_theme_and_background(root, settings)

    def update_settings():
        bg_value = bg_entry.get()
        bg_type = "image" if bg_value.endswith((".png", ".jpg", ".jpeg")) else "color"
        theme_value = theme_var.get()

        settings.update({"background_type": bg_type, "background_value": bg_value, "theme": theme_value})
        save_settings(settings)
        apply_theme_and_background(root, settings)

    settings_frame = ctk.CTkFrame(root, corner_radius=10)
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    bg_label = ctk.CTkLabel(settings_frame, text="Arka Plan Ayarı", font=("Arial", 12))
    bg_label.pack(pady=5)

    bg_entry = ctk.CTkEntry(settings_frame, placeholder_text="Renk Kodu veya Resim Dosya Yolu")
    bg_entry.insert(0, settings["background_value"])
    bg_entry.pack(pady=5)

    theme_var = tk.StringVar(value=settings.get("theme", "dark"))
    theme_label = ctk.CTkLabel(settings_frame, text="Tema Seçimi", font=("Arial", 12))
    theme_label.pack(pady=5)

    theme_dark = ctk.CTkRadioButton(settings_frame, text="Koyu Tema", variable=theme_var, value="dark")
    theme_dark.pack(pady=5)

    theme_light = ctk.CTkRadioButton(settings_frame, text="Açık Tema", variable=theme_var, value="light")
    theme_light.pack(pady=5)

    save_button = ctk.CTkButton(settings_frame, text="Kaydet", command=update_settings)
    save_button.pack(pady=10)


# Ana Arayüz
def main_interface():
    root = ctk.CTk()
    root.title("Dinleme Verisi Analizörü")
    root.geometry("900x600")
    root.resizable(True, True)

    settings = load_settings()
    apply_theme_and_background(root, settings)

    select_dir_btn = ctk.CTkButton(root, text="Klasör Seç ve Verileri Göster", command=lambda: choose_directory(root, settings))
    select_dir_btn.pack(pady=20)

    settings_btn = ctk.CTkButton(root, text="Ayarlar", command=lambda: settings_menu(root))
    settings_btn.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main_interface()
