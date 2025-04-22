# app/gui/main_window.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk
import os

class MainWindow:
    """
    Uygulamanın ana pencere arayüzü
    """
    
    def __init__(self, root, app_manager):
        self.root = root
        self.app_manager = app_manager
        print(f"MainWindow init: source_folder = {self.app_manager.source_folder}")
        print(f"MainWindow init: destination_folder = {self.app_manager.destination_folder}")
        
        # GUI bileşenleri
        self.source_entry = None
        self.dest_entry = None
        self.quality_slider = None
        self.quality_label = None
        self.filesize_label = None
        self.format_var = None
        self.preview_file_combo = None
        self.preview_size_combo = None
        self.preview_canvas = None
        self.preview_label = None
        self.crop_instructions = None
        self.crop_control_var = None
        self.reset_crop_button = None
        self.progress = None
        self.status_label = None
        self.process_button = None
        
        # Boyut onay kutuları
        self.size_checkbuttons = []
        
        # Ekleme kontrol değişkenleri
        self.text_enabled_var = tk.BooleanVar(value=False)
        self.text_var = tk.StringVar(value="")
        self.text_size_var = tk.IntVar(value=24)
        self.text_position_var = tk.StringVar(value="bottom")
        self.text_opacity_var = tk.IntVar(value=100)
        self.text_font_var = tk.StringVar(value="Arial")
        
        self.graphic_enabled_var = tk.BooleanVar(value=False)
        self.graphic_path_var = tk.StringVar(value="")
        self.graphic_position_var = tk.StringVar(value="bottom-right")
        self.graphic_size_var = tk.IntVar(value=20)
        self.graphic_opacity_var = tk.IntVar(value=100)
        
        # Şekil ekleme kontrol değişkenleri
        self.shapes_enabled_var = tk.BooleanVar(value=False)
        self.current_shape_type = tk.StringVar(value="rectangle")
        self.shape_fill_color = (255, 0, 0)  # Kırmızı
        self.shape_outline_color = (0, 0, 0)  # Siyah
        self.shape_outline_width_var = tk.IntVar(value=2)
        self.shape_fill_enabled_var = tk.BooleanVar(value=True)
        self.shape_outline_enabled_var = tk.BooleanVar(value=True)
        
        # Şekil çizim değişkenleri
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.current_shape = None
        self.temp_shape_points = []  # Polygon için noktalar
        
        # Renk değişkenleri
        self.text_color = (255, 255, 255)
        self.text_outline_color = (0, 0, 0)
        self.text_outline_width_var = tk.IntVar(value=1)
        
        # Önizleme değişkenleri
        self.preview_file_var = tk.StringVar()
        self.preview_size_var = tk.StringVar(value="Featured (1200x600)")
        self.preview_img = None
        self.original_preview_width = 0
        self.original_preview_height = 0
        self.current_size_index = 0
        
        # Sürükleme değişkenleri
        self.drag_start_x = None
        self.drag_start_y = None
        self.dragging = False
        
        # Metin ve grafik sürükleme değişkenleri
        self.text_dragging = False
        self.text_drag_start_x = None
        self.text_drag_start_y = None
        self.text_position_manual = False
        self.text_x_position = 0.5  # Merkez olarak başla (0-1 aralığı)
        self.text_y_position = 0.9  # Alt olarak başla (0-1 aralığı)
        
        self.graphic_dragging = False
        self.graphic_drag_start_x = None
        self.graphic_drag_start_y = None
        self.graphic_position_manual = False
        self.graphic_x_position = 0.9  # Sağ olarak başla (0-1 aralığı)
        self.graphic_y_position = 0.9  # Alt olarak başla (0-1 aralığı)
        
        # Callback fonksiyonlarını ayarla
        self.app_manager.on_status_update = self.update_status
        self.app_manager.on_progress_update = self.update_progress
        
        # Arayüzü oluştur
        self.setup_ui()

    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ana içerik çerçevesini oluştur (sol ve sağ bölmelere ayrılacak)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol bölme (görüntü ayarları için)
        left_pane = ttk.Frame(content_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
# Sağ bölme (metin ve grafik ayarları için)
        right_pane = ttk.Frame(content_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=10)
        
        # Sol bölme içeriğini oluştur (görüntü ayarları)
        self.setup_image_settings(left_pane)
        
        # Sağ bölme içeriğini oluştur (metin ve grafik eklemeleri)
        self.setup_overlay_settings(right_pane)
        
        # Alt kısım - ilerleme ve işlem düğmesi
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        # İlerleme çubuğu
        progress_frame = ttk.Frame(bottom_frame)
        progress_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(progress_frame, text="İlerleme:").pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, 
                                    mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Durum etiketi
        self.status_label = ttk.Label(bottom_frame, text="Hazır")
        self.status_label.pack(side=tk.LEFT, pady=5, padx=5)
        

    def setup_image_settings(self, parent_frame):
        """Görüntü ayarları bölümünü oluştur"""
        # Başlık
        ttk.Label(parent_frame, text="Görüntü Ayarları", font=("Arial", 12, "bold")).pack(fill=tk.X, pady=5)
        
        # Kaynak ve hedef klasörler için çerçeve
        folders_frame = ttk.LabelFrame(parent_frame, text="Klasörler")
        folders_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Kaynak klasör seçimi
        source_frame = ttk.Frame(folders_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="Kaynak Klasör:").pack(side=tk.LEFT, padx=5)
        self.source_entry = ttk.Entry(source_frame, width=40)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(source_frame, text="Gözat", command=self.select_source).pack(side=tk.LEFT, padx=5)
        
        # Mevcut kaynak klasör değerini göster
        if self.app_manager.source_folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, self.app_manager.source_folder)
        
        # Hedef klasör seçimi
        dest_frame = ttk.Frame(folders_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="Hedef Klasör:").pack(side=tk.LEFT, padx=5)
        self.dest_entry = ttk.Entry(dest_frame, width=40)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dest_frame, text="Gözat", command=self.select_destination).pack(side=tk.LEFT, padx=5)
        
        # Mevcut hedef klasör değerini göster
        if self.app_manager.destination_folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, self.app_manager.destination_folder)
        
        # Kalite ve format ayarları için çerçeve
        quality_frame = ttk.LabelFrame(parent_frame, text="Kalite ve Format")
        quality_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Kalite kaydırıcısı
        quality_slider_frame = ttk.Frame(quality_frame)
        quality_slider_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_slider_frame, text="JPEG Kalitesi:").pack(side=tk.LEFT, padx=5)
        self.quality_slider = ttk.Scale(quality_slider_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.quality_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.quality_slider.set(self.app_manager.quality)
        self.quality_label = ttk.Label(quality_slider_frame, text=f"{self.app_manager.quality}%")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        # Dosya boyutu tahmini etiketi
        self.filesize_label = ttk.Label(quality_slider_frame, text="Tahmini boyut: --")
        self.filesize_label.pack(side=tk.LEFT, padx=5)
        
        # Kaydırıcıyı hem kaliteyi hem de dosya boyutunu güncellemesi için yapılandır
        self.quality_slider.config(command=self.on_quality_changed)
        
        # Format seçimi
        format_frame = ttk.Frame(quality_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Çıktı Formatı:").pack(side=tk.LEFT, padx=5)
        self.format_var = tk.StringVar(value=self.app_manager.output_format)
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                    values=["Same as input", "JPEG", "PNG", "WebP"])
        format_combo.pack(side=tk.LEFT, padx=5)
        format_combo.bind("<<ComboboxSelected>>", self.on_format_changed)
        
        # Sıfırlama düğmesi
        ttk.Button(format_frame, text="Tümünü Sıfırla", command=self.reset_application).pack(side=tk.RIGHT, padx=5)
        
        # Boyut seçenekleri çerçevesi
        size_frame = ttk.LabelFrame(parent_frame, text="Çıktı Görüntü Boyutları")
        size_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Her bir boyut için onay kutuları oluştur
        size_grid = ttk.Frame(size_frame)
        size_grid.pack(fill=tk.X, pady=5)
        
        for i, (selected, size_data) in enumerate(zip(self.app_manager.selected_sizes, self.app_manager.sizes)):
            width, height, name = size_data
            var = tk.BooleanVar(value=selected)
            cb = ttk.Checkbutton(
                size_grid, 
                text=f"{name} ({width}x{height})", 
                variable=var,
                command=lambda idx=i, v=var: self.on_size_toggled(idx, v)
            )
            
            # 2x2 ızgarada düzenle
            row = i // 2
            col = i % 2
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            self.size_checkbuttons.append((var, cb))
        
        # Önizleme çerçevesi
        preview_frame = ttk.LabelFrame(parent_frame, text="Önizleme")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Önizleme kontrolleri
        preview_control_frame = ttk.Frame(preview_frame)
        preview_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(preview_control_frame, text="Görüntü Seç:").pack(side=tk.LEFT, padx=5)
        self.preview_file_combo = ttk.Combobox(preview_control_frame, textvariable=self.preview_file_var, width=25)
        self.preview_file_combo.pack(side=tk.LEFT, padx=5)
        self.preview_file_combo.bind("<<ComboboxSelected>>", self.on_preview_file_changed)
        
        ttk.Label(preview_control_frame, text="Önizleme Boyutu:").pack(side=tk.LEFT, padx=5)
        
        # Boyut seçim aşağı açılır menüsü için değerleri oluştur
        size_combo_values = [f"{name} ({width}x{height})" for width, height, name in self.app_manager.sizes]
        self.preview_size_combo = ttk.Combobox(preview_control_frame, textvariable=self.preview_size_var, width=15,
                                                values=size_combo_values)
        self.preview_size_combo.pack(side=tk.LEFT, padx=5)
        self.preview_size_combo.bind("<<ComboboxSelected>>", self.on_preview_size_changed)
        
        ttk.Button(preview_control_frame, text="Yenile", command=self.update_preview_files).pack(side=tk.LEFT, padx=5)
        
        # Kırpma kontrolü için ikinci satır
        crop_control_frame = ttk.Frame(preview_frame)
        crop_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.crop_control_var = tk.BooleanVar(value=False)
        self.crop_checkbox = ttk.Checkbutton(crop_control_frame, text="Özel Kırpma Etkinleştir", 
                                        variable=self.crop_control_var, command=self.toggle_crop_control)
        self.crop_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Kırpma sıfırlama düğmesi
        self.reset_crop_button = ttk.Button(crop_control_frame, text="Kırpmayı Sıfırla", 
                                        command=self.reset_crop, state=tk.DISABLED)
        self.reset_crop_button.pack(side=tk.LEFT, padx=5)
        
        # Önizleme tuval çerçevesi
        self.preview_canvas_frame = ttk.Frame(preview_frame)
        self.preview_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(self.preview_canvas_frame, width=600, height=300, bg="light gray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Fare olaylarını bağla - sürükle bırak desteği için
        self.preview_canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.preview_label = ttk.Label(preview_frame, text="Önizleme mevcut değil")
        self.preview_label.pack(padx=5, pady=5)
        
        # Talimat etiketi
        self.crop_instructions = ttk.Label(preview_frame, 
                                        text="Özel kırpma etkinleştirin ve kırpma merkez noktasını ayarlamak için görüntü üzerinde sürükleyin")
        self.crop_instructions.pack(padx=5, pady=2)

    def setup_overlay_settings(self, parent_frame):
        """Metin ve grafik ekleme ayarları bölümünü oluştur"""
        # Başlık
        ttk.Label(parent_frame, text="Metin ve Grafikler", font=("Arial", 12, "bold")).pack(fill=tk.X, pady=5)
        
        # Notebook (sekmeli panel) oluştur
        notebook = ttk.Notebook(parent_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metin sekmesi
        text_tab = ttk.Frame(notebook)
        notebook.add(text_tab, text="Metin")
        
        # Şekil sekmesi (yeni)
        shape_tab = ttk.Frame(notebook)
        notebook.add(shape_tab, text="Şekiller")
        
        # Grafik sekmesi
        graphic_tab = ttk.Frame(notebook)
        notebook.add(graphic_tab, text="Grafik")
        
        # Her sekmenin içeriğini oluştur
        self.setup_text_tab(text_tab)
        self.setup_shape_tab(shape_tab)  # Yeni şekil sekmesi
        self.setup_graphic_tab(graphic_tab)
        
        # İşlem düğmesini alt kısıma ekle
        process_frame = ttk.Frame(parent_frame)
        process_frame.pack(fill=tk.X, pady=20)
    
        self.process_button = ttk.Button(process_frame, text="Görüntüleri İşle", 
                             command=self.start_processing)
        self.process_button.pack(fill=tk.X, padx=5, pady=10)
        
    def setup_text_tab(self, parent_frame):
        """Metin sekmesini oluştur"""
        # Metin ekleme bölümü
        text_frame = ttk.Frame(parent_frame)
        text_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Metin eklemeyi etkinleştir
        text_enable_frame = ttk.Frame(text_frame)
        text_enable_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(text_enable_frame, text="Metin Eklemesini Etkinleştir", 
                    variable=self.text_enabled_var, 
                    command=self.on_text_overlay_toggled).pack(side=tk.LEFT, padx=5)
        
        # Sürükle bırak ile konumlandırma seçeneği
        ttk.Label(text_enable_frame, text="Konumlandırmak için sürükleyin", foreground="blue").pack(side=tk.RIGHT, padx=5)
        
        # Metin girişi
        text_input_frame = ttk.Frame(text_frame)
        text_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_input_frame, text="Metin:").pack(side=tk.LEFT, padx=5)
        text_entry = ttk.Entry(text_input_frame, textvariable=self.text_var, width=30)
        text_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        text_entry.bind("<KeyRelease>", lambda e: self.on_text_settings_changed())
        
        # Metin boyutu ve fontu
        text_format_frame = ttk.Frame(text_frame)
        text_format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_format_frame, text="Boyut:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(text_format_frame, from_=8, to=72, textvariable=self.text_size_var, width=5,
                command=self.on_text_settings_changed).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(text_format_frame, text="Font:").pack(side=tk.LEFT, padx=5)
        font_combo = ttk.Combobox(text_format_frame, textvariable=self.text_font_var, width=12,
                                values=["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana"])
        font_combo.pack(side=tk.LEFT, padx=5)
        font_combo.bind("<<ComboboxSelected>>", lambda e: self.on_text_settings_changed())
        
        # Metin rengi ve dış çizgi
        text_color_frame = ttk.Frame(text_frame)
        text_color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_color_frame, text="Metin Rengi:").pack(side=tk.LEFT, padx=5)
        self.text_color_btn = tk.Button(text_color_frame, bg=self._rgb_to_hex(self.text_color), width=3,
                                    command=self.select_text_color)
        self.text_color_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(text_color_frame, text="Dış Çizgi:").pack(side=tk.LEFT, padx=5)
        self.text_outline_btn = tk.Button(text_color_frame, bg=self._rgb_to_hex(self.text_outline_color), width=3,
                                    command=self.select_outline_color)
        self.text_outline_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(text_color_frame, text="Kalınlık:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(text_color_frame, from_=0, to=5, textvariable=self.text_outline_width_var, width=3,
                command=self.on_text_settings_changed).pack(side=tk.LEFT, padx=5)
        
        # Metin konumu (önizlemede sürükle bırak ile eşleşmesi için devre dışı bırakılabilir)
        text_pos_frame = ttk.Frame(text_frame)
        text_pos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_pos_frame, text="Konum:").pack(side=tk.LEFT, padx=5)
        pos_combo = ttk.Combobox(text_pos_frame, textvariable=self.text_position_var, width=10,
                                values=["top", "center", "bottom", "custom"])
        pos_combo.pack(side=tk.LEFT, padx=5)
        pos_combo.bind("<<ComboboxSelected>>", lambda e: self.on_text_position_changed())
        
        # Metin opaklığı
        text_opacity_frame = ttk.Frame(text_frame)
        text_opacity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_opacity_frame, text="Opaklık:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(text_opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                variable=self.text_opacity_var, command=lambda s: self.on_text_settings_changed()).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Önizleme güncelleme ve metin sıfırlama düğmeleri
        text_button_frame = ttk.Frame(text_frame)
        text_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(text_button_frame, text="Önizlemeyi Güncelle", 
                  command=self.update_preview_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(text_button_frame, text="Metni Sıfırla", 
                  command=self.reset_text_overlay).pack(side=tk.LEFT, padx=5)
    
    def setup_shape_tab(self, parent_frame):
        """Şekil sekmesini oluştur"""
        # Şekil ekleme bölümü
        shape_frame = ttk.Frame(parent_frame)
        shape_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Şekil eklemeyi etkinleştir
        shape_enable_frame = ttk.Frame(shape_frame)
        shape_enable_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(shape_enable_frame, text="Şekil Eklemesini Etkinleştir", 
                    variable=self.shapes_enabled_var, 
                    command=self.on_shapes_enabled_toggled).pack(side=tk.LEFT, padx=5)
        
        # Şekil çizimi için talimat
        ttk.Label(shape_enable_frame, text="Görüntü üzerinde sürükleyerek şekil çizin", 
                 foreground="blue").pack(side=tk.RIGHT, padx=5)
        
        # Şekil türü seçimi
        shape_type_frame = ttk.Frame(shape_frame)
        shape_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(shape_type_frame, text="Şekil Türü:").pack(side=tk.LEFT, padx=5)
        shape_type_combo = ttk.Combobox(shape_type_frame, textvariable=self.current_shape_type, width=15,
                                       values=["rectangle", "ellipse", "line", "polygon", "parallelogram"])
        shape_type_combo.pack(side=tk.LEFT, padx=5)
        shape_type_combo.bind("<<ComboboxSelected>>", self.on_shape_type_changed)
        
        # Şekil dolgu rengi ve çizgisi
        shape_color_frame = ttk.Frame(shape_frame)
        shape_color_frame.pack(fill=tk.X, pady=5)
        
        # Dolgu için onay kutusu ve renk seçimi
        fill_frame = ttk.Frame(shape_color_frame)
        fill_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(fill_frame, text="Dolgu", 
                      variable=self.shape_fill_enabled_var).pack(side=tk.LEFT)
                      
        self.shape_fill_btn = tk.Button(fill_frame, bg=self._rgb_to_hex(self.shape_fill_color), width=3,
                                      command=self.select_shape_fill_color)
        self.shape_fill_btn.pack(side=tk.LEFT, padx=5)
        
        # Dış çizgi için onay kutusu, renk ve kalınlık
        outline_frame = ttk.Frame(shape_color_frame)
        outline_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(outline_frame, text="Dış Çizgi", 
                      variable=self.shape_outline_enabled_var).pack(side=tk.LEFT)
                      
        self.shape_outline_btn = tk.Button(outline_frame, bg=self._rgb_to_hex(self.shape_outline_color), width=3,
                                        command=self.select_shape_outline_color)
        self.shape_outline_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(outline_frame, text="Kalınlık:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(outline_frame, from_=1, to=10, textvariable=self.shape_outline_width_var, width=3).pack(side=tk.LEFT)
        
        # Şekiller listesi
        shape_list_frame = ttk.LabelFrame(shape_frame, text="Çizilen Şekiller")
        shape_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Şekil listesi ve silme düğmesi için çerçeve
        list_control_frame = ttk.Frame(shape_list_frame)
        list_control_frame.pack(fill=tk.X, pady=5)
        
        # Şekil listesi (Listbox)
        self.shape_listbox = tk.Listbox(list_control_frame, height=6)
        self.shape_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(list_control_frame, orient="vertical", command=self.shape_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.shape_listbox.config(yscrollcommand=scrollbar.set)
        
        # Şekil silme düğmesi
        shape_buttons_frame = ttk.Frame(shape_list_frame)
        shape_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(shape_buttons_frame, text="Seçilen Şekli Sil", 
                  command=self.delete_selected_shape).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(shape_buttons_frame, text="Tüm Şekilleri Temizle", 
                  command=self.clear_all_shapes).pack(side=tk.LEFT, padx=5)
        
        # Önizleme güncelleme düğmesi
        shape_preview_frame = ttk.Frame(shape_frame)
        shape_preview_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(shape_preview_frame, text="Önizlemeyi Güncelle", 
                  command=self.update_preview_image).pack(side=tk.LEFT, padx=5)
    
    def setup_graphic_tab(self, parent_frame):
        """Grafik sekmesini oluştur"""
        # Grafik ekleme bölümü
        graphic_frame = ttk.Frame(parent_frame)
        graphic_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Grafik eklemeyi etkinleştir
        graphic_enable_frame = ttk.Frame(graphic_frame)
        graphic_enable_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(graphic_enable_frame, text="Grafik Eklemesini Etkinleştir", 
                    variable=self.graphic_enabled_var, 
                    command=self.on_graphic_overlay_toggled).pack(side=tk.LEFT, padx=5)
        
        # Sürükle bırak ile konumlandırma seçeneği
        ttk.Label(graphic_enable_frame, text="Konumlandırmak için sürükleyin", foreground="blue").pack(side=tk.RIGHT, padx=5)
        
        # Grafik dosyası seçimi
        graphic_select_frame = ttk.Frame(graphic_frame)
        graphic_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(graphic_select_frame, text="Grafik:").pack(side=tk.LEFT, padx=5)
        graphic_entry = ttk.Entry(graphic_select_frame, textvariable=self.graphic_path_var, width=30)
        graphic_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(graphic_select_frame, text="Gözat", 
                command=self.select_graphic_file).pack(side=tk.LEFT, padx=5)
        
        # Grafik konumu (önizlemede sürükle bırak ile eşleşmesi için devre dışı bırakılabilir)
        graphic_pos_frame = ttk.Frame(graphic_frame)
        graphic_pos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(graphic_pos_frame, text="Konum:").pack(side=tk.LEFT, padx=5)
        graphic_pos_combo = ttk.Combobox(graphic_pos_frame, textvariable=self.graphic_position_var, width=12,
                                        values=["top-left", "top-right", "center", "bottom-left", "bottom-right", "custom"])
        graphic_pos_combo.pack(side=tk.LEFT, padx=5)
        graphic_pos_combo.bind("<<ComboboxSelected>>", lambda e: self.on_graphic_position_changed())
        
        # Grafik boyutu
        graphic_size_frame = ttk.Frame(graphic_frame)
        graphic_size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(graphic_size_frame, text="Boyut (%):").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(graphic_size_frame, from_=1, to=100, textvariable=self.graphic_size_var, width=5,
                command=self.on_graphic_settings_changed).pack(side=tk.LEFT, padx=5)
        
        # Grafik opaklığı
        graphic_opacity_frame = ttk.Frame(graphic_frame)
        graphic_opacity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(graphic_opacity_frame, text="Opaklık:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(graphic_opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                variable=self.graphic_opacity_var, command=lambda s: self.on_graphic_settings_changed()).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
# Önizleme güncelleme ve grafik sıfırlama düğmeleri
        graphic_button_frame = ttk.Frame(graphic_frame)
        graphic_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(graphic_button_frame, text="Önizlemeyi Güncelle", 
                  command=self.update_preview_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(graphic_button_frame, text="Grafiği Sıfırla", 
                  command=self.reset_graphic_overlay).pack(side=tk.LEFT, padx=5)
                  
    # ŞEKIL IŞLEMLERI IÇIN YENI METOTLAR
    
    def on_shapes_enabled_toggled(self):
        """Şekil eklemesi etkinleştirildiğinde/devre dışı bırakıldığında çağrılır"""
        is_enabled = self.shapes_enabled_var.get()
        self.app_manager.overlay_manager.set_shapes_enabled(is_enabled)
        
        if is_enabled:
            self.crop_instructions.config(text=f"Şekil çizme modu: {self.current_shape_type}. Görüntü üzerinde sürükleyin.")
        else:
            self.crop_instructions.config(text="Şekil çizme modu devre dışı.")
            
        self.update_preview_image()
    
    def on_shape_type_changed(self, event=None):
        """Şekil türü değiştiğinde çağrılır"""
        shape_type = self.current_shape_type.get()
        
        if shape_type == "polygon":
            self.crop_instructions.config(text="Çokgen çizme modu: Köşeleri eklemek için tıklayın. Son noktaya tekrar tıklayarak tamamlayın.")
        elif shape_type == "parallelogram":
            self.crop_instructions.config(text="Paralelkenar çizme modu: Bir köşeden sürüklemeye başlayın.")
        else:
            self.crop_instructions.config(text=f"Şekil çizme modu: {shape_type}. Görüntü üzerinde sürükleyin.")
    
    def select_shape_fill_color(self):
        """Şekil dolgu rengi seçme iletişim kutusunu aç"""
        current_color = self._rgb_to_hex(self.shape_fill_color)
        color = colorchooser.askcolor(color=current_color, title="Dolgu Rengi Seç")
        
        if color[1]:  # ikinci element hex renk değeri
            self.shape_fill_btn.config(bg=color[1])
            # RGB rengini 0-255 aralığına ölçeklendir
            r, g, b = [int(x) for x in color[0]]
            self.shape_fill_color = (r, g, b)
    
    def select_shape_outline_color(self):
        """Şekil dış çizgi rengi seçme iletişim kutusunu aç"""
        current_color = self._rgb_to_hex(self.shape_outline_color)
        color = colorchooser.askcolor(color=current_color, title="Dış Çizgi Rengi Seç")
        
        if color[1]:  # ikinci element hex renk değeri
            self.shape_outline_btn.config(bg=color[1])
            # RGB rengini 0-255 aralığına ölçeklendir
            r, g, b = [int(x) for x in color[0]]
            self.shape_outline_color = (r, g, b)
    
    def delete_selected_shape(self):
        """Seçilen şekli sil"""
        selected_idx = self.shape_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.app_manager.overlay_manager.remove_shape(idx)
            self.update_shape_list()
            self.update_preview_image()
    
    def clear_all_shapes(self):
        """Tüm şekilleri temizle"""
        if messagebox.askyesno("Şekilleri Temizle", "Tüm şekilleri silmek istediğinizden emin misiniz?"):
            self.app_manager.overlay_manager.clear_shapes()
            self.update_shape_list()
            self.update_preview_image()
    
    def update_shape_list(self):
        """Şekil listesini güncelle"""
        shapes = self.app_manager.overlay_manager.shapes
        self.shape_listbox.delete(0, tk.END)
        
        for i, shape in enumerate(shapes):
            shape_type = shape.get('type', 'bilinmeyen')
            self.shape_listbox.insert(tk.END, f"{i+1}. {shape_type}")
    
    def reset_text_overlay(self):
        """Metin ayarlarını sıfırla"""
        self.text_enabled_var.set(False)
        self.text_var.set("")
        self.text_size_var.set(24)
        self.text_position_var.set("bottom")
        self.text_opacity_var.set(100)
        self.text_font_var.set("Arial")
        self.text_color = (255, 255, 255)
        self.text_outline_color = (0, 0, 0)
        self.text_outline_width_var.set(1)
        self.text_position_manual = False
        
        # Renk düğmelerini güncelle
        self.text_color_btn.config(bg=self._rgb_to_hex(self.text_color))
        self.text_outline_btn.config(bg=self._rgb_to_hex(self.text_outline_color))
        
        # OverlayManager'ı güncelle
        self.app_manager.overlay_manager.set_text_enabled(False)
        
        # Önizlemeyi güncelle
        self.update_preview_image()
    
    def reset_graphic_overlay(self):
        """Grafik ayarlarını sıfırla"""
        self.graphic_enabled_var.set(False)
        self.graphic_path_var.set("")
        self.graphic_position_var.set("bottom-right")
        self.graphic_size_var.set(20)
        self.graphic_opacity_var.set(100)
        self.graphic_position_manual = False
        
        # OverlayManager'ı güncelle
        self.app_manager.overlay_manager.set_graphic_enabled(False)
        
        # Önizlemeyi güncelle
        self.update_preview_image()

    def update_preview_files(self):
        """Önizleme için kullanılabilir dosyaların listesini güncelle"""
        images = self.app_manager.get_image_files()
        
        if not images:
            self.preview_file_combo['values'] = []
            self.preview_file_var.set("")
            self.preview_label.config(text="Kaynak klasörde desteklenen görüntü bulunamadı")
        else:
            self.preview_file_combo['values'] = images
            self.preview_file_var.set(images[0])
            self.on_preview_file_changed()

    def on_preview_file_changed(self, event=None):
        """Önizleme dosyası değiştiğinde çağrılır"""
        self.update_preview_image()

    def on_preview_size_changed(self, event=None):
        """Önizleme boyutu değiştiğinde çağrılır"""
        self.update_preview_image()

    def on_text_position_changed(self):
        """Metin konumu değiştiğinde çağrılır"""
        position = self.text_position_var.get()
        if position == "custom":
            self.text_position_manual = True
            # Manuel konumu etkinleştir
            self.crop_instructions.config(text="METİN eklemesini konumlandırmak için sürükleyin")
        else:
            self.text_position_manual = False
            # OverlayManager'a konumu ayarla
            self.app_manager.overlay_manager.set_text_position(position)
        
        self.update_preview_image()

    def on_graphic_position_changed(self):
        """Grafik konumu değiştiğinde çağrılır"""
        position = self.graphic_position_var.get()
        if position == "custom":
            self.graphic_position_manual = True
            # Manuel konumu etkinleştir
            self.crop_instructions.config(text="GRAFİK eklemesini konumlandırmak için sürükleyin")
        else:
            self.graphic_position_manual = False
            # OverlayManager'a konumu ayarla
            self.app_manager.overlay_manager.set_graphic_position(position)
        
        self.update_preview_image()

    def on_canvas_press(self, event):
        """Fare tuşuna basıldığında çağrılır"""
        if not self.preview_img:
            return
        
        # Tuvaldeki görüntü konumunu hesapla
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        img_x_offset = (canvas_width - self.original_preview_width) // 2
        img_y_offset = (canvas_height - self.original_preview_height) // 2
        
        # Görüntünün sınırlarını hesapla
        img_left = img_x_offset
        img_right = img_x_offset + self.original_preview_width
        img_top = img_y_offset
        img_bottom = img_y_offset + self.original_preview_height
        
        # Basmanın görüntü sınırları içinde olup olmadığını kontrol et
        if img_left <= event.x <= img_right and img_top <= event.y <= img_bottom:
            # Şekil çizim modu
            if self.shapes_enabled_var.get():
                # Göreceli koordinatları hesapla (0-1 aralığında)
                rel_x = (event.x - img_left) / self.original_preview_width
                rel_y = (event.y - img_top) / self.original_preview_height
                
                shape_type = self.current_shape_type.get()
                
                if shape_type == "polygon":
                    # Çokgen çizimi için ilk tıklama veya devam eden tıklamalar
                    if not self.temp_shape_points:
                        # İlk nokta
                        self.temp_shape_points.append((rel_x, rel_y))
                        # İşaretleyici çiz
                        self.preview_canvas.create_oval(
                            event.x-4, event.y-4, event.x+4, event.y+4, 
                            fill="red", tags="temp_shape")
                        self.crop_instructions.config(text="Çokgen: İlk nokta eklendi. Devam etmek için tıklayın veya ilk noktaya tekrar tıklayarak tamamlayın.")
                    else:
                        # İlk noktaya yakın tıklama - çokgeni tamamla
                        first_point = self.temp_shape_points[0]
                        if (abs(rel_x - first_point[0]) < 0.02 and 
                            abs(rel_y - first_point[1]) < 0.02 and
                            len(self.temp_shape_points) > 2):
                            
                            # Çokgeni tamamla
                            self.temp_shape_points.append(first_point)  # Daire tamamla
                            
                            # Fill ve outline renklerini ayarla
                            fill_color = None
                            if self.shape_fill_enabled_var.get():
                                fill_color = self.shape_fill_color
                                
                            outline_color = None
                            if self.shape_outline_enabled_var.get():
                                outline_color = self.shape_outline_color
                            
                            # OverlayManager'a ekle
                            shape_data = {
                                'type': 'polygon',
                                'points': self.temp_shape_points.copy(),
                                'fill_color': fill_color,
                                'outline_color': outline_color,
                                'outline_width': self.shape_outline_width_var.get()
                            }
                            
                            self.app_manager.overlay_manager.add_shape(shape_data)
                            self.update_shape_list()
                            
                            # Geçici noktaları temizle
                            self.temp_shape_points = []
                            self.preview_canvas.delete("temp_shape")
                            
                            # Önizlemeyi güncelle
                            self.update_preview_image()
                            self.crop_instructions.config(text=f"Çokgen tamamlandı. Yeni bir çokgen çizmeye başlayın.")
                        else:
                            # Yeni nokta ekle
                            self.temp_shape_points.append((rel_x, rel_y))
                            
                            # Yeni nokta ve çizgiyi çiz
                            self.preview_canvas.create_oval(
                                event.x-4, event.y-4, event.x+4, event.y+4, 
                                fill="red", tags="temp_shape")
                            
                            # Önceki noktadan bu noktaya çizgi çiz
                            if len(self.temp_shape_points) > 1:
                                prev_point = self.temp_shape_points[-2]
                                prev_x = img_left + int(prev_point[0] * self.original_preview_width)
                                prev_y = img_top + int(prev_point[1] * self.original_preview_height)
                                
                                self.preview_canvas.create_line(
                                    prev_x, prev_y, event.x, event.y, 
                                    fill="red", width=2, tags="temp_shape")
                            
                            self.crop_instructions.config(text=f"Çokgen: {len(self.temp_shape_points)} nokta eklendi.")
                    
                    return
                else:
                    # Diğer şekiller için sürükleme işlemi başlat
                    self.drawing = True
                    self.start_x = rel_x
                    self.start_y = rel_y
                    self.current_shape = shape_type
                    
                    # Eğer paralelkenar ise, eğim faktörünü başlat
                    if shape_type == "parallelogram":
                        self.parallelogram_skew = 0.2  # Varsayılan eğim
                    
                    self.crop_instructions.config(text=f"Şekil çiziyor: {shape_type}. Sürükleyin ve bırakın.")
                    return
            
            # Metin sürükleme algılama - bunu önce kontrol et
            if self.text_enabled_var.get() and self.text_position_manual:
                # Metin konumunu hesapla
                text_x = img_x_offset + int(self.text_x_position * self.original_preview_width)
                text_y = img_y_offset + int(self.text_y_position * self.original_preview_height)
                
                # Fare tıklaması metin etrafındaki bölge içerisinde mi?
                text_radius = 15  # Metin tıklama algılama yarıçapı
                if (text_x - text_radius <= event.x <= text_x + text_radius and 
                    text_y - text_radius <= event.y <= text_y + text_radius):
                    self.text_dragging = True
                    self.text_drag_start_x = event.x
                    self.text_drag_start_y = event.y
                    self.crop_instructions.config(text="METİN eklemesini sürüklüyor...")
                    print("Text dragging started")
                    return
            
            # Grafik sürükleme algılama
            if self.graphic_enabled_var.get() and self.graphic_position_manual:
                # Grafik konumunu hesapla
                graphic_x = img_x_offset + int(self.graphic_x_position * self.original_preview_width)
                graphic_y = img_y_offset + int(self.graphic_y_position * self.original_preview_height)
                
                # Fare tıklaması grafik etrafındaki bölge içerisinde mi?
                graphic_radius = 20  # Grafik tıklama algılama yarıçapı
                if (graphic_x - graphic_radius <= event.x <= graphic_x + graphic_radius and 
                    graphic_y - graphic_radius <= event.y <= graphic_y + graphic_radius):
                    self.graphic_dragging = True
                    self.graphic_drag_start_x = event.x
                    self.graphic_drag_start_y = event.y
                    self.crop_instructions.config(text="GRAFİK eklemesini sürüklüyor...")
                    print("Graphic dragging started")
                    return
            
            # Kırpma modu etkinse
            if self.app_manager.is_cropping_active:
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.dragging = True
                
                # Tıklanma noktasını hemen kırpma merkezi olarak ayarla
                rel_x = (event.x - img_left) / self.original_preview_width
                rel_y = (event.y - img_top) / self.original_preview_height
                self.app_manager.set_crop_center(rel_x, rel_y)
                self.update_preview_image()
                self.crop_instructions.config(text=f"Kırpma merkezi için sürükleyin: ({int(rel_x*100)}%, {int(rel_y*100)}%)")

    def on_canvas_drag(self, event):
        """Fare sürüklendiğinde çağrılır"""
        if not self.preview_img:
            return
            
        # Tuvaldeki görüntü konumunu hesapla
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        img_x_offset = (canvas_width - self.original_preview_width) // 2
        img_y_offset = (canvas_height - self.original_preview_height) // 2
        
        # Görüntünün sınırlarını hesapla
        img_left = img_x_offset
        img_right = img_x_offset + self.original_preview_width
        img_top = img_y_offset
        img_bottom = img_y_offset + self.original_preview_height
        
        # Şekil çizme
        if self.drawing and self.shapes_enabled_var.get():
            # Sürükleme pozisyonunu kısıtla
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Göreceli konumu 0-1 aralığında
            end_x = (x - img_left) / self.original_preview_width
            end_y = (y - img_top) / self.original_preview_height
            
            # Geçici şekli temizle
            self.preview_canvas.delete("temp_shape")
            
            # Geçici şekli çiz
            if self.current_shape == "rectangle":
                # Dikdörtgen çiz
                self.preview_canvas.create_rectangle(
                    img_left + int(self.start_x * self.original_preview_width),
                    img_top + int(self.start_y * self.original_preview_height),
                    x, y,
                    outline="red", width=2, tags="temp_shape"
                )
            elif self.current_shape == "ellipse":
                # Elips çiz
                self.preview_canvas.create_oval(
                    img_left + int(self.start_x * self.original_preview_width),
                    img_top + int(self.start_y * self.original_preview_height),
                    x, y,
                    outline="red", width=2, tags="temp_shape"
                )
            elif self.current_shape == "line":
                # Çizgi çiz
                self.preview_canvas.create_line(
                    img_left + int(self.start_x * self.original_preview_width),
                    img_top + int(self.start_y * self.original_preview_height),
                    x, y,
                    fill="red", width=2, tags="temp_shape"
                )
            elif self.current_shape == "parallelogram":
                # Paralelkenar çiz
                start_x = img_left + int(self.start_x * self.original_preview_width)
                start_y = img_top + int(self.start_y * self.original_preview_height)
                
                # Eğim miktarını hesapla (genişliğin %20'si)
                width = x - start_x
                skew_amount = int(width * self.parallelogram_skew)
                
                # Paralelkenar köşeleri
                points = [
                    start_x + skew_amount, start_y,          # sol üst
                    x + skew_amount, start_y,                # sağ üst
                    x, y,                                    # sağ alt
                    start_x, y                               # sol alt
                ]
                
                self.preview_canvas.create_polygon(
                    points, outline="red", width=2, fill="", tags="temp_shape"
                )
            
            return
        
        # Metin sürükleme
        if self.text_dragging:
            # Yeni konumu hesapla (görüntü sınırları içinde kalacak şekilde)
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Göreceli konumu 0-1 aralığına dönüştür
            self.text_x_position = (x - img_left) / self.original_preview_width
            self.text_y_position = (y - img_top) / self.original_preview_height
            
            # OverlayManager'a konum bilgisini aktar
            self.app_manager.overlay_manager.set_text_position("custom")
            self.app_manager.overlay_manager.set_text_manual_position(
                self.text_x_position, self.text_y_position)
            
            # Metin konumunu güncelle ve yeniden çiz
            self.update_preview_image()
            self.crop_instructions.config(text=f"Metin konumu: ({int(self.text_x_position*100)}%, {int(self.text_y_position*100)}%)")
            return
            
        # Grafik sürükleme
        if self.graphic_dragging:
            # Yeni konumu hesapla (görüntü sınırları içinde kalacak şekilde)
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Göreceli konumu 0-1 aralığına dönüştür
            self.graphic_x_position = (x - img_left) / self.original_preview_width
            self.graphic_y_position = (y - img_top) / self.original_preview_height
            
            # OverlayManager'a konum bilgisini aktar
            self.app_manager.overlay_manager.set_graphic_position("custom")
            self.app_manager.overlay_manager.set_graphic_manual_position(
                self.graphic_x_position, self.graphic_y_position)
            
            # Grafik konumunu güncelle ve yeniden çiz
            self.update_preview_image()
            self.crop_instructions.config(text=f"Grafik konumu: ({int(self.graphic_x_position*100)}%, {int(self.graphic_y_position*100)}%)")
            return
            
        # Kırpma sürükleme
        if self.dragging:
            # Sürükleme pozisyonunu kısıtla
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Yeni pozisyonu göreceli koordinatlara dönüştür
            rel_x = (x - img_left) / self.original_preview_width
            rel_y = (y - img_top) / self.original_preview_height
            
            # Kırpma merkezini güncelle
            self.app_manager.set_crop_center(rel_x, rel_y)
            self.update_preview_image()
            self.crop_instructions.config(text=f"Kırpma merkezi için sürükleyin: ({int(rel_x*100)}%, {int(rel_y*100)}%)")

    def on_canvas_release(self, event):
        """Fare tuşu bırakıldığında çağrılır"""
        # Şekil çizimi tamamlama
        if self.drawing and self.shapes_enabled_var.get():
            # Tuvaldeki görüntü konumunu hesapla
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            img_x_offset = (canvas_width - self.original_preview_width) // 2
            img_y_offset = (canvas_height - self.original_preview_height) // 2
            
            # Görüntünün sınırlarını hesapla
            img_left = img_x_offset
            img_right = img_x_offset + self.original_preview_width
            img_top = img_y_offset
            img_bottom = img_y_offset + self.original_preview_height
            
            # Sürükleme pozisyonunu kısıtla
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Göreceli konumu 0-1 aralığında
            end_x = (x - img_left) / self.original_preview_width
            end_y = (y - img_top) / self.original_preview_height
            
            # Çok küçük şekilleri önle
            min_size = 0.01  # Minimum boyut (görüntünün %1'i)
            if (abs(end_x - self.start_x) < min_size and abs(end_y - self.start_y) < min_size) and self.current_shape != "line":
                self.drawing = False
                self.preview_canvas.delete("temp_shape")
                self.crop_instructions.config(text=f"Şekil çok küçük. Daha büyük bir şekil çizin.")
                return
            
            # Şekil verilerini oluştur
            shape_data = {
                'type': self.current_shape,
                'x1': min(self.start_x, end_x),
                'y1': min(self.start_y, end_y),
                'x2': max(self.start_x, end_x),
                'y2': max(self.start_y, end_y),
                'fill_color': self.shape_fill_color if self.shape_fill_enabled_var.get() else None,
                'outline_color': self.shape_outline_color if self.shape_outline_enabled_var.get() else None,
                'outline_width': self.shape_outline_width_var.get()
            }
            
            # Paralelkenar için özel veriler
            if self.current_shape == "parallelogram":
                shape_data = {
                    'type': 'parallelogram',
                    'x': min(self.start_x, end_x),
                    'y': min(self.start_y, end_y),
                    'w': abs(end_x - self.start_x),
                    'h': abs(end_y - self.start_y),
                    'skew': self.parallelogram_skew,
                    'fill_color': self.shape_fill_color if self.shape_fill_enabled_var.get() else None,
                    'outline_color': self.shape_outline_color if self.shape_outline_enabled_var.get() else None,
                    'outline_width': self.shape_outline_width_var.get()
                }
            
            # Şekli overlay manager'a ekle
            self.app_manager.overlay_manager.add_shape(shape_data)
            self.drawing = False
            
            # Şekil listesini güncelle
            self.update_shape_list()
            
            # Geçici şekli temizle ve önizlemeyi güncelle
            self.preview_canvas.delete("temp_shape")
            self.update_preview_image()
            
            self.crop_instructions.config(text=f"{self.current_shape} şekli eklendi. Yeni şekil çizmeye başlayabilirsiniz.")
            return
        
        # Metin sürükleme
        if self.text_dragging:
            self.text_dragging = False
            self.crop_instructions.config(text=f"Metin konumu şu noktaya ayarlandı: ({int(self.text_x_position*100)}%, {int(self.text_y_position*100)}%)")
            
            # Overlay manager'a konum bilgisini aktar
            self.app_manager.overlay_manager.set_text_position("custom")
            self.app_manager.overlay_manager.set_text_manual_position(
                self.text_x_position, self.text_y_position)
            
            # Seçiciyi güncelle
            self.text_position_var.set("custom")
            print(f"Text position finalized: {self.text_x_position:.2f}, {self.text_y_position:.2f}")
            return
            
# Grafik sürükleme
        if self.graphic_dragging:
            self.graphic_dragging = False
            self.crop_instructions.config(text=f"Grafik konumu şu noktaya ayarlandı: ({int(self.graphic_x_position*100)}%, {int(self.graphic_y_position*100)}%)")
            
            # Overlay manager'a konum bilgisini aktar
            self.app_manager.overlay_manager.set_graphic_position("custom")
            self.app_manager.overlay_manager.set_graphic_manual_position(
                self.graphic_x_position, self.graphic_y_position)
            
            # Seçiciyi güncelle
            self.graphic_position_var.set("custom")
            print(f"Graphic position finalized: {self.graphic_x_position:.2f}, {self.graphic_y_position:.2f}")
            return
            
        # Kırpma sürükleme
        if self.dragging:
            self.dragging = False
            
            # Tuval üzerindeki son pozisyonu al (kısıtlanmış)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            img_x_offset = (canvas_width - self.original_preview_width) // 2
            img_y_offset = (canvas_height - self.original_preview_height) // 2
            
            img_left = img_x_offset
            img_right = img_x_offset + self.original_preview_width
            img_top = img_y_offset
            img_bottom = img_y_offset + self.original_preview_height
            
            x = max(img_left, min(event.x, img_right))
            y = max(img_top, min(event.y, img_bottom))
            
            # Son pozisyonu göreceli koordinatlara dönüştür
            rel_x = (x - img_left) / self.original_preview_width
            rel_y = (y - img_top) / self.original_preview_height
            
            # Kırpma merkezini ayarla ve önizlemeyi güncelle
            self.app_manager.set_crop_center(rel_x, rel_y)
            self.update_preview_image()
            self.crop_instructions.config(text=f"Kırpma merkezi şu noktaya ayarlandı: ({int(rel_x*100)}%, {int(rel_y*100)}%)")

    def update_preview_image(self):
        """Seçilen dosya ve boyuta göre önizleme görüntüsünü güncelle"""
        selected_file = self.preview_file_var.get()
        selected_size_str = self.preview_size_var.get()
        
        if not selected_file or not selected_size_str:
            # Dosya veya boyut seçilmemişse işlemi atla
            self.preview_canvas.delete("all")
            self.preview_label.config(text="Dosya veya boyut seçilmedi")
            return
        
        # Boyut dizesinden indeksi çıkar
        size_index = 0  # Varsayılan değer
        found_size = False
        
        for i, (width, height, name) in enumerate(self.app_manager.sizes):
            if f"{name} ({width}x{height})" == selected_size_str:
                size_index = i
                self.current_size_index = i
                found_size = True
                break
        
        if not found_size:
            # Boyut bulunamazsa öne çıkan görüntü boyutunu varsayılan olarak kullan
            size_index = 0
            self.current_size_index = 0
        
        # AppManager'dan önizleme görüntüsünü yükle
        try:
            original_img, resized_img, original_file_size, estimated_size = self.app_manager.load_preview_image(
                selected_file, size_index
            )
            
            if original_img is None or resized_img is None:
                self.preview_canvas.delete("all")
                self.preview_label.config(text="Önizleme yüklenirken hata oluştu")
                return
                
            # Önizleme için küçült
            width, height, _ = self.app_manager.sizes[size_index]
            
            # Tuval boyutunu al
            max_preview_width = self.preview_canvas.winfo_width() - 10
            max_preview_height = self.preview_canvas.winfo_height() - 10
            
            if max_preview_width <= 1 or max_preview_height <= 1:
                # Tuval henüz gerçekleştirilmemiş, varsayılan boyutları kullan
                max_preview_width = 590
                max_preview_height = 290
            
            scale_factor = min(max_preview_width / width, max_preview_height / height)
            
            preview_width = int(width * scale_factor)
            preview_height = int(height * scale_factor)
            
            # Tıklama konumu hesaplaması için orijinal önizleme boyutunu sakla
            self.original_preview_width = preview_width
            self.original_preview_height = preview_height
            
            # Manuel metin konumlandırma
            if self.text_enabled_var.get() and self.text_position_manual:
                # Özel metin konumu kullan
                self.app_manager.overlay_manager.set_text_position("custom")
                self.app_manager.overlay_manager.set_text_manual_position(
                    self.text_x_position, self.text_y_position)
            else:
                # Normal metin konumu kullan
                self.app_manager.overlay_manager.set_text_position(self.text_position_var.get())
            
            # Manuel grafik konumlandırma
            if self.graphic_enabled_var.get() and self.graphic_position_manual:
                # Özel grafik konumu kullan
                self.app_manager.overlay_manager.set_graphic_position("custom")
                self.app_manager.overlay_manager.set_graphic_manual_position(
                    self.graphic_x_position, self.graphic_y_position)
            else:
                # Normal grafik konumu kullan
                self.app_manager.overlay_manager.set_graphic_position(self.graphic_position_var.get())
            
            # Eklemeleri uygula
            preview_img = resized_img.resize((preview_width, preview_height), Image.LANCZOS)
            
            # Görüntüyü tkinter PhotoImage'e dönüştür
            self.preview_img = ImageTk.PhotoImage(preview_img)
            
            # Tuvali güncelle
            self.preview_canvas.delete("all")
            
            # Tuvalde görüntü konumunu hesapla
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Tuval henüz gerçekleştirilmemiş
                canvas_width = 600
                canvas_height = 300
            
            img_x = canvas_width // 2
            img_y = canvas_height // 2
            
            self.preview_canvas.create_image(img_x, img_y, image=self.preview_img, anchor=tk.CENTER, tags="preview")
            
            # Manuel metin konumu için gösterge
            if self.text_enabled_var.get() and self.text_position_manual:
                # Hesaplanan konumda metin göstergesi çiz
                x_pos = img_x - (preview_width // 2) + int(self.text_x_position * preview_width)
                y_pos = img_y - (preview_height // 2) + int(self.text_y_position * preview_height)
                
                # Daha belirgin bir metin konumu göstergesi çiz
                # Arka plan daire
                self.preview_canvas.create_oval(
                    x_pos-15, y_pos-15, x_pos+15, y_pos+15,
                    fill="blue", outline="white", width=2, tags="text_overlay"
                )
                
                # İç daire
                self.preview_canvas.create_oval(
                    x_pos-7, y_pos-7, x_pos+7, y_pos+7,
                    fill="white", outline="blue", width=1, tags="text_overlay"
                )
                
                # Metin etiket
                self.preview_canvas.create_text(
                    x_pos, y_pos-25,
                    text="Metin Konumu",
                    fill="white", font=("Arial", 10, "bold"),
                    tags="text_overlay"
                )
                
                # Koordinat bilgisi
                self.preview_canvas.create_text(
                    x_pos, y_pos+25,
                    text=f"({int(self.text_x_position*100)}%, {int(self.text_y_position*100)}%)",
                    fill="white", font=("Arial", 8),
                    tags="text_overlay"
                )

            # Manuel grafik konumu için gösterge
            if self.graphic_enabled_var.get() and self.graphic_position_manual:
                # Hesaplanan konumda grafik göstergesi çiz
                x_pos = img_x - (preview_width // 2) + int(self.graphic_x_position * preview_width)
                y_pos = img_y - (preview_height // 2) + int(self.graphic_y_position * preview_height)
                
                # Daha belirgin bir grafik konumu göstergesi çiz
                # Arka plan kare
                self.preview_canvas.create_rectangle(
                    x_pos-15, y_pos-15, x_pos+15, y_pos+15,
                    fill="green", outline="white", width=2, tags="graphic_overlay"
                )
                
                # İç kare
                self.preview_canvas.create_rectangle(
                    x_pos-7, y_pos-7, x_pos+7, y_pos+7,
                    fill="white", outline="green", width=1, tags="graphic_overlay"
                )
                
                # Grafik etiket
                self.preview_canvas.create_text(
                    x_pos, y_pos-25,
                    text="Grafik Konumu",
                    fill="white", font=("Arial", 10, "bold"),
                    tags="graphic_overlay"
                )
                
                # Koordinat bilgisi
                self.preview_canvas.create_text(
                    x_pos, y_pos+25,
                    text=f"({int(self.graphic_x_position*100)}%, {int(self.graphic_y_position*100)}%)",
                    fill="white", font=("Arial", 8),
                    tags="graphic_overlay"
                )
            
            # Özel kırpma etkinse kırpma merkezi işaretçisini çiz
            if (self.app_manager.is_cropping_active and 
                self.app_manager.crop_center_x is not None and 
                self.app_manager.crop_center_y is not None):
                
                marker_x = img_x - (preview_width // 2) + int(self.app_manager.crop_center_x * preview_width)
                marker_y = img_y - (preview_height // 2) + int(self.app_manager.crop_center_y * preview_height)
                
                # Daha belirgin bir işaretçi çiz (artı işareti ile birlikte daire)
                marker_size = 12
                
                # Dış daire (işaretçi arka planı)
                self.preview_canvas.create_oval(
                    marker_x - marker_size - 2, marker_y - marker_size - 2,
                    marker_x + marker_size + 2, marker_y + marker_size + 2,
                    fill="white", outline="black", width=1, tags="marker"
                )
                
                # Artı işareti
                self.preview_canvas.create_line(marker_x - marker_size, marker_y, 
                                            marker_x + marker_size, marker_y, 
                                            fill="red", width=2, tags="marker")
                self.preview_canvas.create_line(marker_x, marker_y - marker_size, 
                                            marker_x, marker_y + marker_size, 
                                            fill="red", width=2, tags="marker")
                
                # Merkezdeki daire
                self.preview_canvas.create_oval(
                    marker_x - 5, marker_y - 5, 
                    marker_x + 5, marker_y + 5, 
                    fill="red", outline="white", width=1, tags="marker"
                )
                
                # Tahmini kırpma bölgesini çiz
                self.draw_crop_region_preview()
            
            # Bilgi etiketini güncelle
            original_size = original_img.size
            
            # Dosya boyutlarını formatla
            from app.utils.file_utils import get_file_size_str
            original_size_str = get_file_size_str(original_file_size)
            estimated_size_str = get_file_size_str(estimated_size)
            
            # En boy oranlarını hesapla
            original_ratio = original_size[0] / original_size[1]
            target_ratio = width / height
            
            if abs(original_ratio - target_ratio) < 0.01:
                crop_info = "Kırpma gerekmez"
            elif original_ratio > target_ratio:
                crop_info = "Genişlik kırpılacak"
            else:
                crop_info = "Yükseklik kırpılacak"
            
            # Ekleme bilgisi
            overlay_info = ""
            if self.app_manager.overlay_manager.text_enabled:
                overlay_info += " | Metin eklemesi etkin"
            if self.app_manager.overlay_manager.graphic_enabled:
                overlay_info += " | Grafik eklemesi etkin"
            if self.app_manager.overlay_manager.shapes_enabled:
                overlay_info += f" | Şekil eklemesi etkin ({len(self.app_manager.overlay_manager.shapes)} şekil)"
                
            self.preview_label.config(
                text=f"Orijinal: {original_size[0]}x{original_size[1]} ({original_size_str}) | "
                    f"Hedef: {width}x{height} | {crop_info}{overlay_info}"
            )
            
            # Dosya boyutu tahminini güncelle
            self.filesize_label.config(text=f"Tahmini boyut: {estimated_size_str}")
            
            # AppManager'ın geçerli önizleme dosyasını ve boyutunu sakla
            self.app_manager.current_preview_file = selected_file
            self.app_manager.current_preview_size = (width, height)
            
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_label.config(text=f"Önizleme hatası: {str(e)}")
            print(f"Preview error: {str(e)}")

    def draw_crop_region_preview(self):
        """Tahmini kırpma bölgesini tuvalde göster"""
        if (not self.app_manager.is_cropping_active or
            self.app_manager.crop_center_x is None or
            self.app_manager.crop_center_y is None):
            return
        
        try:
            # Canvas boyutlarını al
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Önizleme görüntüsünün konumunu hesapla
            img_x = canvas_width // 2
            img_y = canvas_height // 2
            
            # Kırpma merkezi koordinatlarını hesapla
            marker_x = img_x - (self.original_preview_width // 2) + int(self.app_manager.crop_center_x * self.original_preview_width)
            marker_y = img_y - (self.original_preview_height // 2) + int(self.app_manager.crop_center_y * self.original_preview_height)
            
            # Kırpma alanının köşelerini hesapla
            left = marker_x - (self.original_preview_width // 2)
            right = left + self.original_preview_width
            top = marker_y - (self.original_preview_height // 2)
            bottom = top + self.original_preview_height
            
            # Tuval sınırlarını kontrol et
            img_left = img_x - (self.original_preview_width // 2)
            img_right = img_x + (self.original_preview_width // 2)
            img_top = img_y - (self.original_preview_height // 2)
            img_bottom = img_y + (self.original_preview_height // 2)
            
            # Kırpma alanını tuval sınırlarına kısıtla
            left = max(img_left, left)
            right = min(img_right, right)
            top = max(img_top, top)
            bottom = min(img_bottom, bottom)
            
            # Kırpma alanını göster
            self.preview_canvas.create_rectangle(
                left, top, right, bottom,
                outline="yellow", width=2, dash=(5, 5), tags="crop_preview"
            )
        except Exception as e:
            print(f"Error drawing crop region: {str(e)}")

    def on_text_overlay_toggled(self):
        """Metin eklemesi etkinleştirildiğinde/devre dışı bırakıldığında çağrılır"""
        is_enabled = self.text_enabled_var.get()
        self.app_manager.overlay_manager.set_text_enabled(is_enabled)
        self.update_preview_image()

    def on_text_settings_changed(self, event=None):
        """Metin ayarları değiştiğinde çağrılır"""
        # OverlayManager'a ayarları uygula
        overlay_mgr = self.app_manager.overlay_manager
        overlay_mgr.set_text(self.text_var.get())
        overlay_mgr.set_text_size(self.text_size_var.get())
        overlay_mgr.set_text_font(self.text_font_var.get())
        overlay_mgr.set_text_position(self.text_position_var.get())
        overlay_mgr.set_text_opacity(self.text_opacity_var.get())
        overlay_mgr.set_text_outline_width(self.text_outline_width_var.get())
        
        # Önizlemeyi güncelle
        self.update_preview_image()

    def on_graphic_overlay_toggled(self):
        """Grafik eklemesi etkinleştirildiğinde/devre dışı bırakıldığında çağrılır"""
        is_enabled = self.graphic_enabled_var.get()
        self.app_manager.overlay_manager.set_graphic_enabled(is_enabled)
        self.update_preview_image()

    def on_graphic_settings_changed(self, event=None):
        """Grafik ayarları değiştiğinde çağrılır"""
        # OverlayManager'a ayarları uygula
        overlay_mgr = self.app_manager.overlay_manager
        overlay_mgr.set_graphic_position(self.graphic_position_var.get())
        overlay_mgr.set_graphic_size(self.graphic_size_var.get())
        overlay_mgr.set_graphic_opacity(self.graphic_opacity_var.get())
        
        # Önizlemeyi güncelle
        self.update_preview_image()

    def select_text_color(self):
        """Metin rengi seçme iletişim kutusunu aç"""
        current_color = self._rgb_to_hex(self.text_color)
        color = colorchooser.askcolor(color=current_color, title="Metin Rengi Seç")
        
        if color[1]:  # ikinci element hex renk değeri
            self.text_color_btn.config(bg=color[1])
            # RGB rengini 0-255 aralığına ölçeklendir
            r, g, b = [int(x) for x in color[0]]
            self.text_color = (r, g, b)
            self.app_manager.overlay_manager.set_text_color(self.text_color)
            self.update_preview_image()

    def select_outline_color(self):
        """Metin kontur rengi seçme iletişim kutusunu aç"""
        current_color = self._rgb_to_hex(self.text_outline_color)
        color = colorchooser.askcolor(color=current_color, title="Dış Çizgi Rengi Seç")
        
        if color[1]:  # ikinci element hex renk değeri
            self.text_outline_btn.config(bg=color[1])
            # RGB rengini 0-255 aralığına ölçeklendir
            r, g, b = [int(x) for x in color[0]]
            self.text_outline_color = (r, g, b)
            self.app_manager.overlay_manager.set_text_outline_color(self.text_outline_color)
            self.update_preview_image()

    def select_graphic_file(self):
        """Grafik dosyası seçme iletişim kutusunu aç"""
        filetypes = [
            ("Resim dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("PNG dosyaları", "*.png"),
            ("JPEG dosyaları", "*.jpg *.jpeg"),
            ("Tüm dosyalar", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="Grafik Dosyası Seç", filetypes=filetypes)
        
        if file_path:
            self.graphic_path_var.set(file_path)
            success = self.app_manager.overlay_manager.set_graphic(file_path)
            
            if success:
                self.update_preview_image()
            else:
                messagebox.showerror("Hata", "Seçilen grafik dosyası yüklenemedi")

    def reset_overlays(self):
        """Tüm ekleme ayarlarını sıfırla"""
        # Metin ayarlarını sıfırla
        self.reset_text_overlay()
        
        # Grafik ayarlarını sıfırla
        self.reset_graphic_overlay()
        
        # Şekil ayarlarını sıfırla
        self.shapes_enabled_var.set(False)
        self.app_manager.overlay_manager.clear_shapes()
        self.app_manager.overlay_manager.set_shapes_enabled(False)
        self.update_shape_list()
        
        # Önizlemeyi güncelle
        self.update_preview_image()

    def _rgb_to_hex(self, rgb):
        """RGB rengini hex renk koduna dönüştürür"""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def select_source(self):
        """Kaynak klasörü seçme iletişim kutusunu göster"""
        # Kaynak klasör için browsing iletişim kutusunu açarken input klasörüyle başla
        folder = filedialog.askdirectory(title="Kaynak Klasör Seç", 
                                          initialdir=self.app_manager.source_folder)
        if folder:
            self.app_manager.set_source_folder(folder)
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.update_preview_files()

    def select_destination(self):
        """Hedef klasörü seçme iletişim kutusunu göster"""
        # Hedef klasör için browsing iletişim kutusunu açarken output klasörüyle başla
        folder = filedialog.askdirectory(title="Hedef Klasör Seç", 
                                        initialdir=self.app_manager.destination_folder)
        if folder:
            self.app_manager.set_destination_folder(folder)
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)

    def on_quality_changed(self, event=None):
        """Kalite kaydırıcısı değiştiğinde tetiklenir"""
        quality = int(float(self.quality_slider.get()))
        self.app_manager.set_quality(quality)
        self.quality_label.config(text=f"{quality}%")
        self.update_file_size_estimation()

    def on_format_changed(self, event=None):
        """Format aşağı açılır menüsü değiştiğinde tetiklenir"""
        format_name = self.format_var.get()
        self.app_manager.set_output_format(format_name)
        self.update_file_size_estimation()

    def on_size_toggled(self, index, var):
        """Boyut onay kutusu değiştiğinde tetiklenir"""
        self.app_manager.toggle_size(index, var.get())

    def update_file_size_estimation(self):
        """Dosya boyutu tahminini güncelle"""
        # Önizleme görüntüsü zaten yüklendiyse yeniden yükle
        if self.app_manager.current_preview_file and self.app_manager.current_original_img:
            self.update_preview_image()

    def toggle_crop_control(self):
        """Özel kırpma kontrolünü etkinleştir/devre dışı bırak"""
        is_active = self.crop_control_var.get()
        self.app_manager.set_crop_active(is_active)
        
        if is_active:
            self.reset_crop_button.config(state=tk.NORMAL)
            self.crop_instructions.config(text="Kırpma merkez noktasını ayarlamak için görüntüde sürükleyin")
        else:
            self.reset_crop_button.config(state=tk.DISABLED)
            self.crop_instructions.config(text="Özel kırpma etkinleştirin ve kırpma merkez noktasını ayarlamak için görüntüde sürükleyin")
            
        self.update_preview_image()

    def reset_crop(self):
        """Kırpma merkezini sıfırla"""
        self.app_manager.reset_crop()
        self.update_preview_image()

    def reset_application(self):
        """Tüm uygulama ayarlarını varsayılana sıfırla"""
        # Onay için sor
        if messagebox.askyesno("Uygulamayı Sıfırla", "Tüm ayarları sıfırlamak istediğinizden emin misiniz?"):
            # Kaliteyi sıfırla
            self.app_manager.set_quality(85)
            self.quality_slider.set(85)
            self.quality_label.config(text="85%")
            
            # Formatı sıfırla
            self.app_manager.set_output_format("JPEG")
            self.format_var.set("JPEG")
            
            # Boyut seçimlerini sıfırla (yalnızca öne çıkan görüntü seçili)
            for i in range(len(self.app_manager.selected_sizes)):
                is_selected = (i == 0)  # Yalnızca ilk boyutu seç (Featured)
                self.app_manager.selected_sizes[i] = is_selected
                self.size_checkbuttons[i][0].set(is_selected)
            
            # Kırpma ayarlarını sıfırla
            self.crop_control_var.set(False)
            self.toggle_crop_control()
            
            # Önizlemeyi sıfırla
            self.preview_size_var.set(f"{self.app_manager.sizes[0][2]} ({self.app_manager.sizes[0][0]}x{self.app_manager.sizes[0][1]})")
            
            # Ekleme ayarlarını sıfırla
            self.reset_overlays()
            
            # Dosya boyutu tahminini güncelle
            self.update_file_size_estimation()
            self.status_label.config(text="Uygulama varsayılan ayarlara sıfırlandı")

    def update_status(self, message):
        """Durum etiketini güncelle (AppManager'dan çağrılır)"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
            
        # İşlem tamamlandıysa düğmeyi yeniden etkinleştir
        if message == "All images processed successfully!":
            messagebox.showinfo("Tamamlandı", "Görüntü optimizasyonu başarıyla tamamlandı!")
            self.process_button.config(state=tk.NORMAL)
        elif message.startswith("Error"):
            messagebox.showerror("Hata", message) 
            self.process_button.config(state=tk.NORMAL)

    def update_progress(self, value):
        """İlerleme çubuğunu güncelle (AppManager'dan çağrılır)"""
        self.progress['value'] = value
        self.root.update_idletasks()

    def start_processing(self):
        """Görüntü işleme sürecini başlat"""
        # Kaynak ve hedef klasörleri girişlerden al
        self.app_manager.set_source_folder(self.source_entry.get())
        self.app_manager.set_destination_folder(self.dest_entry.get())
        
        # Girişi doğrula
        if not self.app_manager.source_folder or not os.path.isdir(self.app_manager.source_folder):
            messagebox.showerror("Hata", "Lütfen geçerli bir kaynak klasör seçin")
            return
        
        if not self.app_manager.destination_folder or not os.path.isdir(self.app_manager.destination_folder):
            messagebox.showerror("Hata", "Lütfen geçerli bir hedef klasör seçin")
            return
        
        # En az bir boyutun seçili olup olmadığını kontrol et
        if not any(self.app_manager.selected_sizes):
            messagebox.showerror("Hata", "Lütfen en az bir çıktı boyutu seçin")
            return
        
        # İşlem düğmesini devre dışı bırak
        self.process_button.config(state=tk.DISABLED)
        
        # İşlemeyi başlat
        self.app_manager.process_images()