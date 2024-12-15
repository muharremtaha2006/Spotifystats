import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
from PIL import Image, ImageTk
import customtkinter as ctk

# CustomTkinter temasını ayarlama
ctk.set_appearance_mode("dark")  # "dark" veya "light"
ctk.set_default_color_theme("blue")  # Tema: "blue", "green", "dark-blue"

# Ayarlar dosyası yolu
SETTINGS_FILE = "settings.json"

# Varsayılan ayarlar
DEFAULT_SETTINGS = {
    "background_type": "color",  # "color" veya "image"
    "background_value": "black",  # Renk kodu ya da dosya yolu
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def apply_background(root, settings):
    """Arka planı ayarlara göre uygular."""
    if settings["background_type"] == "color":
        root.configure(bg=settings["background_value"])
    elif settings["background_type"] == "image":
        try:
            bg_image = Image.open(settings["background_value"])
            bg_image = bg_image.resize((root.winfo_width(), root.winfo_height()), Image.ANTIALIAS)
            bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(root, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Arka plan resmi yüklenemedi: {e}")
            root.configure(bg="black")  # Varsayılan renge dön

def settings_menu(root, current_settings):
    """Ayarlar menüsünü oluşturur."""
    settings_window = ctk.CTkToplevel(root)
    settings_window.title("Ayarlar")
    settings_window.geometry("400x300")

    # Renk seçimi
    def set_color(color):
        current_settings["background_type"] = "color"
        current_settings["background_value"] = color
        save_settings(current_settings)
        apply_background(root, current_settings)

    def choose_image():
        file_path = filedialog.askopenfilename(title="Arkaplan Resmi Seç",
                                               filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            current_settings["background_type"] = "image"
            current_settings["background_value"] = file_path
            save_settings(current_settings)
            apply_background(root, current_settings)

    def reset_background():
        current_settings.update(DEFAULT_SETTINGS)
        save_settings(current_settings)
        apply_background(root, current_settings)

    # Başlık
    title_label = ctk.CTkLabel(settings_window, text="Arka Plan Ayarları", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Renk seçenekleri
    color_frame = ctk.CTkFrame(settings_window)
    color_frame.pack(pady=10, fill=tk.X)

    ctk.CTkButton(color_frame, text="Siyah", command=lambda: set_color("black")).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(color_frame, text="Beyaz", command=lambda: set_color("white")).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(color_frame, text="Gri", command=lambda: set_color("#333333")).pack(side=tk.LEFT, padx=5, pady=5)

    # Resim seçimi
    image_button = ctk.CTkButton(settings_window, text="Resim Seç", command=choose_image)
    image_button.pack(pady=10)

    # Varsayılan ayarları geri yükle
    reset_button = ctk.CTkButton(settings_window, text="Varsayılanlara Dön", command=reset_background)
    reset_button.pack(pady=10)

    # Kapat düğmesi
    close_button = ctk.CTkButton(settings_window, text="Kapat", command=settings_window.destroy)
    close_button.pack(pady=10)

def display_data(analyzed_data):
    root = ctk.CTk()
    root.title("Toplam Dinleme Süreleri")
    root.geometry("1000x600")

    # Ayarlar yüklenir
    current_settings = load_settings()

    # Arka plan uygulanır
    apply_background(root, current_settings)

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

    settings_button = ctk.CTkButton(title_bar, text="⚙", width=30, fg_color="#1a1a1a",
                                    command=lambda: settings_menu(root, current_settings))
    settings_button.place(x=880, y=5)

    # Şarkılar tablosu
    frame = ctk.CTkFrame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    columns = ("Şarkı Adı", "Sanatçı", "Albüm", "Toplam Dinleme Süresi (dk)")
    tree = ctk.CTkScrollableFrame(frame, width=950, height=450)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    header_frame = ctk.CTkFrame(tree)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    for col in columns:
        header = ctk.CTkLabel(header_frame, text=col, font=("Arial", 12, "bold"))
        header.pack(side="left", padx=50)

    for item in analyzed_data:
        row_frame = ctk.CTkFrame(tree)
        row_frame.pack(fill=tk.X, pady=5)

        ctk.CTkLabel(row_frame, text=item["track_name"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=item["artist"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=item["album"], font=("Arial", 10)).pack(side="left", padx=50)
        ctk.CTkLabel(row_frame, text=str(item["total_minutes"]), font=("Arial", 10)).pack(side="left", padx=50)

    root.mainloop()
