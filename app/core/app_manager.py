# app/core/app_manager.py
import os
import threading
from PIL import Image
import io
from app.core.image_processor import ImageProcessor
from app.utils.file_utils import get_file_size_str
from app.core.overlay_manager import OverlayManager

class AppManager:
    """
    Uygulama mantığını ve durumunu yöneten sınıf
    """
    
    def __init__(self):
        # Görüntü işleme motoru
        self.image_processor = ImageProcessor()
        
        # Ekleme yöneticisi
        self.overlay_manager = OverlayManager()
        
        # Kaynak ve hedef klasörler
        self.source_folder = "input"  # Kaynak klasör "input" olarak ayarlandı
        self.destination_folder = "output"  # Hedef klasör "output" olarak ayarlandı
        
        # Kalite ayarı
        self.quality = 85
        
        # Çıktı formatı
        self.output_format = "JPEG"
        
        # Desteklenen formatlar
        self.supported_formats = [".jpg", ".jpeg", ".png"]
        
        # Boyutlar
        self.sizes = [
            (1200, 600, "Featured"),  # Featured image
            (800, 600, "Large"),      # Large content image
            (600, 400, "Medium"),     # Medium content image
            (300, 200, "Thumbnail")   # Thumbnail
        ]
        
        # Seçilen boyutlar
        self.selected_sizes = [True, False, False, False]
        
        # Kırpma merkezi
        self.crop_center_x = None
        self.crop_center_y = None
        self.is_cropping_active = False
        
        # Önizleme bilgisi
        self.current_preview_file = None
        self.current_preview_size = None
        self.current_original_img = None
        
        # İşlem durumu için callback fonksiyonları
        self.on_status_update = None
        self.on_progress_update = None
    
    def get_image_files(self):
        """
        Kaynak klasördeki tüm desteklenen görüntü dosyalarını döndürür
        """
        if not self.source_folder or not os.path.isdir(self.source_folder):
            return []
            
        image_files = []
        for filename in os.listdir(self.source_folder):
            ext = os.path.splitext(filename)[1].lower()
            if ext in self.supported_formats:
                image_files.append(filename)
                
        return image_files
    
    def set_source_folder(self, folder):
        """Kaynak klasörünü ayarla"""
        self.source_folder = folder
    
    def set_destination_folder(self, folder):
        """Hedef klasörünü ayarla"""
        self.destination_folder = folder
    
    def set_quality(self, quality):
        """Kalite ayarını güncelle"""
        self.quality = quality
    
    def set_output_format(self, format_name):
        """Çıktı formatını ayarla"""
        self.output_format = format_name
    
    def set_crop_active(self, active):
        """Özel kırpma modunu etkinleştir/devre dışı bırak"""
        self.is_cropping_active = active
        
        # Kırpma devre dışıysa merkezi sıfırla
        if not active:
            self.crop_center_x = None
            self.crop_center_y = None
            print("Crop mode disabled, reset crop center to None")
        else:
            print("Crop mode enabled")
    
    def set_crop_center(self, x, y):
        """Kırpma merkezini ayarla"""
        if not self.is_cropping_active:
            print("Warning: Trying to set crop center when crop mode is not active")
            return
            
        self.crop_center_x = x
        self.crop_center_y = y
        print(f"Crop center set to: x={x}, y={y}")
    
    def reset_crop(self):
        """Kırpma merkezini sıfırla"""
        self.crop_center_x = None
        self.crop_center_y = None
        print("Crop center reset to None")
    
    def toggle_size(self, index, value):
        """Belirli boyut seçimini değiştir"""
        if 0 <= index < len(self.selected_sizes):
            self.selected_sizes[index] = value
    
    def load_preview_image(self, filename, size_index):
        """
        Belirli bir görüntüyü önizleme için yükler
        """
        if not self.source_folder or not filename:
            return None, None, None, None
            
        try:
            img_path = os.path.join(self.source_folder, filename)
            original_img = Image.open(img_path)
            self.current_original_img = original_img.copy()
            
            width, height, name = self.sizes[size_index]
            
            # Görüntüyü yeniden boyutlandır ve kırp
            resized_img = self.image_processor.resize_image_with_custom_crop(
                original_img, 
                width, 
                height, 
                self.crop_center_x, 
                self.crop_center_y
            )
            
            # Metin ve grafik eklemeleri uygula
            resized_img = self.overlay_manager.apply_overlay(resized_img)
            
            # Orijinal dosya boyutunu al
            original_file_size = os.path.getsize(img_path)
            
            # Tahmini dosya boyutunu hesapla
            estimated_size = self.estimate_file_size(resized_img)
            
            return original_img, resized_img, original_file_size, estimated_size
            
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            return None, None, 0, 0
    
    def estimate_file_size(self, img):
        """
        Belirli bir görüntünün mevcut ayarlarla tahmini dosya boyutunu hesaplar
        """
        if img is None:
            return 0
            
        try:
            # Geçici bir bellek arabelleğine kaydet
            img_byte_arr = io.BytesIO()
            
            # Formata göre kaydet
            if self.output_format == "JPEG":
                img.save(img_byte_arr, format='JPEG', quality=self.quality, optimize=True)
            elif self.output_format == "PNG":
                img.save(img_byte_arr, format='PNG', optimize=True)
            elif self.output_format == "WebP":
                img.save(img_byte_arr, format='WebP', quality=self.quality, optimize=True)
            else:
                # Varsayılan olarak JPEG
                img.save(img_byte_arr, format='JPEG', quality=self.quality, optimize=True)
            
            # Boyutu al
            size_bytes = img_byte_arr.tell()
            return size_bytes
            
        except Exception as e:
            print(f"Error estimating file size: {str(e)}")
            return 0
    
    def process_images(self):
        """
        Tüm görüntüleri işleme başlat
        """
        threading.Thread(target=self._process_images_thread, daemon=True).start()
    
    def _process_images_thread(self):
        """
        Arka planda görüntüleri işle
        """
        try:
            # Görüntü dosyalarını bul
            images = self.get_image_files()
            
            if not images:
                if self.on_status_update:
                    self.on_status_update("No supported images found in the source folder")
                return
            
            if self.on_status_update:
                self.on_status_update(f"Found {len(images)} images. Processing...")
            
            # İlerleme çubuğu için toplam işlemleri hesapla
            selected_sizes_count = sum(1 for s in self.selected_sizes if s)
            total_operations = len(images) * selected_sizes_count
            completed = 0
            
            # Her görüntüyü işle
            for img_file in images:
                try:
                    # Görüntüyü aç
                    img_path = os.path.join(self.source_folder, img_file)
                    img = Image.open(img_path)
                    filename, ext = os.path.splitext(img_file)
                    
                    # Özel kırpma merkezini sadece önizleme dosyası için kullan
                    use_custom_crop = (self.is_cropping_active and 
                                    self.crop_center_x is not None and 
                                    self.crop_center_y is not None and 
                                    img_file == self.current_preview_file)
                    
                    # Çıktı formatını belirle
                    if self.output_format == "Same as input":
                        out_ext = ext
                        save_format = None
                    elif self.output_format == "JPEG":
                        out_ext = ".jpg"
                        save_format = "JPEG"
                    elif self.output_format == "PNG":
                        out_ext = ".png"
                        save_format = "PNG"
                    elif self.output_format == "WebP":
                        out_ext = ".webp"
                        save_format = "WebP"
                    
                    # Her seçilen boyut için işle
                    for i, (selected, size_data) in enumerate(zip(self.selected_sizes, self.sizes)):
                        if selected:
                            width, height, size_name = size_data
                            
                            # Özel kırpma kullan (uygulanabilirse)
                            if use_custom_crop:
                                resized_img = self.image_processor.resize_image_with_custom_crop(
                                    img.copy(), 
                                    width, height, 
                                    self.crop_center_x, 
                                    self.crop_center_y
                                )
                            else:
                                resized_img = self.image_processor.resize_image_with_custom_crop(
                                    img.copy(), 
                                    width, height, 
                                    None, None
                                )
                            
                            # Metin ve grafik eklemeleri uygula
                            resized_img = self.overlay_manager.apply_overlay(resized_img)
                            
                            # Boyuta özgü alt klasör oluştur
                            size_folder = f"{width}x{height}"
                            out_folder = os.path.join(self.destination_folder, size_folder)
                            os.makedirs(out_folder, exist_ok=True)
                            
                            # Görüntüyü kaydet
                            out_file = os.path.join(out_folder, f"{filename}{out_ext}")
                            
                            # Orijinal ve yeni dosya boyutlarını takip et
                            orig_size = os.path.getsize(img_path)
                            
                            if save_format in ["JPEG", "WebP"]:
                                resized_img.save(out_file, format=save_format, quality=self.quality, optimize=True)
                            elif save_format == "PNG":
                                resized_img.save(out_file, format="PNG", optimize=True)
                            else:  # Same as input
                                if ext.lower() in ['.jpg', '.jpeg']:
                                    resized_img.save(out_file, quality=self.quality, optimize=True)
                                else:
                                    resized_img.save(out_file, optimize=True)
                            
                            # Yeni dosya boyutunu al
                            new_size = os.path.getsize(out_file)
                            reduction = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0
                            
                            completed += 1
                            progress = (completed / total_operations) * 100
                            
                            # İlerleme güncellemesi
                            if self.on_progress_update:
                                self.on_progress_update(progress)
                            
                            # Dosya boyutlarını gösterim için biçimlendir
                            orig_size_str = get_file_size_str(orig_size)
                            new_size_str = get_file_size_str(new_size)
                            
                            crop_info = ""
                            if use_custom_crop:
                                crop_info = " (with custom crop)"
                                
                            overlay_info = ""
                            if self.overlay_manager.text_enabled or self.overlay_manager.graphic_enabled:
                                overlay_info = " (with overlays)"
                                
                            # Durum güncellemesi
                            if self.on_status_update:
                                self.on_status_update(
                                    f"Processed {completed}/{total_operations}: {img_file} ({width}x{height})"
                                    f"{crop_info}{overlay_info} - {orig_size_str} → {new_size_str} ({reduction:.1f}% smaller)"
                                )
                
                except Exception as e:
                    if self.on_status_update:
                        self.on_status_update(f"Error processing {img_file}: {str(e)}")
            
            if self.on_status_update:
                self.on_status_update("All images processed successfully!")
                self.on_progress_update(100)  # İlerleme çubuğunu tamamla
        
        except Exception as e:
            if self.on_status_update:
                self.on_status_update(f"Error: {str(e)}")