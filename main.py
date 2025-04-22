# main.py
import tkinter as tk
from tkinter import ttk
import os
from app.gui.main_window import MainWindow
from app.core.app_manager import AppManager

def main():
    """
    Ana uygulama giriş noktası
    """
    print("Uygulama başlatılıyor...")
    
    root = tk.Tk()
    root.title("WordPress Image Optimizer")
    root.geometry("1920x1080")
    root.resizable(True, True)
    
    # Tk stil yapılandırması
    style = ttk.Style()
    style.theme_use('clam')  # veya 'alt', 'default', 'classic' gibi diğer temalar
    
    # Uygulama yöneticisi oluştur
    app_manager = AppManager()
    
    # Klasör yollarını hazırla
    input_path = os.path.abspath("input")
    output_path = os.path.abspath("output")
    graphics_path = os.path.abspath("graphics")
    
    print(f"Kaynak klasör yolu: {input_path}")
    print(f"Hedef klasör yolu: {output_path}")
    print(f"Grafikler klasör yolu: {graphics_path}")
    
    # AppManager'daki değerleri göster
    print(f"Başlangıçta AppManager source_folder: {app_manager.source_folder}")
    print(f"Başlangıçta AppManager destination_folder: {app_manager.destination_folder}")
    
    # Kaynak ve hedef klasörleri ayarla
    app_manager.set_source_folder(input_path)
    app_manager.set_destination_folder(output_path)
    
    # Ayarlama sonrası değerleri göster
    print(f"Ayarlama sonrası AppManager source_folder: {app_manager.source_folder}")
    print(f"Ayarlama sonrası AppManager destination_folder: {app_manager.destination_folder}")
    
    # Ana pencereyi oluştur
    app = MainWindow(root, app_manager)
    
    # Uygulamayı başlat
    root.mainloop()

if __name__ == "__main__":
    # Gerekli klasörleri kontrol et
    os.makedirs("app", exist_ok=True)
    os.makedirs("app/core", exist_ok=True)
    os.makedirs("app/gui", exist_ok=True)
    os.makedirs("app/utils", exist_ok=True)
    os.makedirs("input", exist_ok=True)  # "input" klasörünü oluştur
    os.makedirs("output", exist_ok=True)  # "output" klasörünü oluştur
    os.makedirs("graphics", exist_ok=True)  # "graphics" klasörünü oluştur (grafikler için)
    
    main()