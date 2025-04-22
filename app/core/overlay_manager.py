# app/core/overlay_manager.py
from PIL import Image, ImageDraw, ImageFont
import os
import math

class OverlayManager:
    """
    Görüntülere metin ve grafik eklemelerini yönetmek için sınıf
    """
    
    def __init__(self):
        # Metin ayarları
        self.text = ""
        self.text_size = 24
        self.text_color = (255, 255, 255)  # Beyaz
        self.text_outline_color = (0, 0, 0)  # Siyah
        self.text_outline_width = 1
        self.text_position = "bottom"  # bottom, top, center
        self.text_opacity = 100  # 0-100
        self.text_font = "Arial"
        self.text_enabled = False
        
        # Grafik eklemeleri
        self.graphic_path = None
        self.graphic_position = "bottom-right"  # bottom-right, bottom-left, top-right, top-left, center
        self.graphic_size = 20  # Hedef görüntünün yüzde kaçı
        self.graphic_opacity = 100  # 0-100
        self.graphic_enabled = False
        self.graphic_image = None
        
        # Eklenmiş fontu sakla
        self._cached_font = None
        self._cached_font_size = None
        
        # Manuel metin konumlandırma için yeni özellikler
        self.text_position_manual = False
        self.text_x_position = 0.5  # Merkez (0-1 aralığı)
        self.text_y_position = 0.9  # Alt (0-1 aralığı)
        
        # Manuel grafik konumlandırma için yeni özellikler
        self.graphic_position_manual = False
        self.graphic_x_position = 0.9  # Sağ (0-1 aralığı)
        self.graphic_y_position = 0.9  # Alt (0-1 aralığı)
        
        # Temel şekiller için yeni özellikler
        self.shapes = []  # Şekil listesi
        self.shapes_enabled = False  # Şekillerin etkinlik durumu
            # Metinler için liste yapısı
        self.texts = []  # Metin listesi
        
        # Eski metin özelliklerini geriye dönük uyumluluk için tutun
        self.text = ""
        self.text_size = 24
        self.text_color = (255, 255, 255)  # Beyaz
        self.text_outline_color = (0, 0, 0)  # Siyah  
        self.text_outline_width = 1
        self.text_position = "bottom"  # bottom, top, center
        self.text_opacity = 100  # 0-100
        self.text_font = "Arial"
        self.text_enabled = False
        self.text_position_manual = False
        self.text_x_position = 0.5  # Merkez (0-1 aralığı)
        self.text_y_position = 0.9  # Alt (0-1 aralığı)        
    def set_text(self, text):
        """Eklenecek metni ayarla"""
        self.text = text
    
    def set_text_size(self, size):
        """Metin boyutunu ayarla"""
        self.text_size = size
        # Önbelleği temizle
        self._cached_font = None
        self._cached_font_size = None
    
    def set_text_color(self, color):
        """Metin rengini ayarla, RGB tuple olarak"""
        self.text_color = color
    
    def set_text_outline_color(self, color):
        """Metin dış çizgi rengini ayarla"""
        self.text_outline_color = color
    
    def set_text_outline_width(self, width):
        """Metin dış çizgi kalınlığını ayarla"""
        self.text_outline_width = width
    
    def set_text_position(self, position):
        """Metin konumunu ayarla"""
        if position == "custom":
            self.text_position_manual = True
        else:
            self.text_position_manual = False
            self.text_position = position
    
    def set_text_manual_position(self, x, y):
        """Metinin özel konumunu ayarla (0-1 aralığında x, y değerleri)"""
        self.text_x_position = max(0, min(1, x))
        self.text_y_position = max(0, min(1, y))
    
    def set_text_opacity(self, opacity):
        """Metin opaklığını ayarla (0-100)"""
        self.text_opacity = max(0, min(100, opacity))
    
    def set_text_font(self, font_name):
        """Metin fontunu ayarla"""
        self.text_font = font_name
        # Önbelleği temizle
        self._cached_font = None
        self._cached_font_size = None
    
    def set_text_enabled(self, enabled):
        """Metin eklemeyi etkinleştir/devre dışı bırak"""
        self.text_enabled = enabled
    
    def set_graphic(self, path):
        """Eklenecek grafik dosyasını ayarla"""
        if path and os.path.exists(path):
            self.graphic_path = path
            try:
                self.graphic_image = Image.open(path).convert("RGBA")
                return True
            except Exception as e:
                print(f"Error loading graphic image: {str(e)}")
                self.graphic_path = None
                self.graphic_image = None
                return False
        else:
            self.graphic_path = None
            self.graphic_image = None
            return False
    
    def set_graphic_position(self, position):
        """Grafik konumunu ayarla"""
        if position == "custom":
            self.graphic_position_manual = True
        else:
            self.graphic_position_manual = False
            self.graphic_position = position
    
    def set_graphic_manual_position(self, x, y):
        """Grafiğin özel konumunu ayarla (0-1 aralığında x, y değerleri)"""
        self.graphic_x_position = max(0, min(1, x))
        self.graphic_y_position = max(0, min(1, y))
    
    def set_graphic_size(self, size_percent):
        """Grafik boyutunu hedef görüntünün yüzdesi olarak ayarla"""
        self.graphic_size = max(1, min(100, size_percent))
    
    def set_graphic_opacity(self, opacity):
        """Grafik opaklığını ayarla (0-100)"""
        self.graphic_opacity = max(0, min(100, opacity))
    
    def set_graphic_enabled(self, enabled):
        """Grafik eklemeyi etkinleştir/devre dışı bırak"""
        self.graphic_enabled = enabled
    
    # YENİ EKLENEN METOTLAR - TEMEL ŞEKİLLER İÇİN
    
    def set_shapes_enabled(self, enabled):
        """Şekil eklemeyi etkinleştir/devre dışı bırak"""
        self.shapes_enabled = enabled
    
    def add_shape(self, shape_data):
        """Şekil verilerini listeye ekle"""
        self.shapes.append(shape_data)
    
    def clear_shapes(self):
        """Tüm şekilleri temizle"""
        self.shapes = []
    
    def remove_shape(self, index):
        """Belirli bir şekli kaldır"""
        if 0 <= index < len(self.shapes):
            self.shapes.pop(index)
            
    def _get_font(self, base_size=None):
        """
        Belirtilen boyut için font nesnesi döndürür
        """
        size = base_size if base_size is not None else self.text_size
        
        # Önbellekten font varsa ve boyutu aynıysa kullan
        if self._cached_font and self._cached_font_size == size:
            return self._cached_font
        
        try:
            # Windows için sistem font dizinini bul
            if os.name == 'nt':  # Windows
                font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                font_files = {
                    'arial': os.path.join(font_dir, 'arial.ttf'),
                    'times new roman': os.path.join(font_dir, 'times.ttf'),
                    'courier new': os.path.join(font_dir, 'cour.ttf'),
                    'georgia': os.path.join(font_dir, 'georgia.ttf'),
                    'verdana': os.path.join(font_dir, 'verdana.ttf')
                }
                
                font_name = self.text_font.lower()
                if font_name in font_files and os.path.exists(font_files[font_name]):
                    font_path = font_files[font_name]
                    font = ImageFont.truetype(font_path, size)
                else:
                    print(f"Font not found in system: {self.text_font}")
                    # Varsayılan PIL fontunu kullan
                    font = ImageFont.load_default()
            else:
                # Linux/Mac için genel font yolları
                # Linux için yaygın font dizinleri
                font_dirs = [
                    '/usr/share/fonts',
                    '/usr/local/share/fonts',
                    os.path.expanduser('~/.fonts')
                ]
                
                # Font adı ile font dosyası adı eşlemesi
                font_name_mapping = {
                    'arial': ['arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf'],
                    'times new roman': ['times.ttf', 'Times.ttf', 'TimesNewRoman.ttf', 'DejaVuSerif.ttf'],
                    'courier new': ['cour.ttf', 'CourierNew.ttf', 'DejaVuSansMono.ttf'],
                    'georgia': ['georgia.ttf', 'Georgia.ttf'],
                    'verdana': ['verdana.ttf', 'Verdana.ttf']
                }
                
                # Eşleşen font adlarını bul
                font_name = self.text_font.lower()
                font_path = None
                
                if font_name in font_name_mapping:
                    for dir_path in font_dirs:
                        if font_path:
                            break
                        for root, dirs, files in os.walk(dir_path):
                            if font_path:
                                break
                            for possible_name in font_name_mapping[font_name]:
                                if possible_name in files:
                                    font_path = os.path.join(root, possible_name)
                                    break
                
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, size)
                else:
                    print(f"Font not found in system: {self.text_font}")
                    # Varsayılan PIL fontunu kullan
                    font = ImageFont.load_default()
            
            # Önbelleğe al
            self._cached_font = font
            self._cached_font_size = size
            
            return font
        except Exception as e:
            print(f"Error loading font: {str(e)}, using default")
            # Varsayılan font (PIL'in dahili fontu)
            return ImageFont.load_default()
    
    def apply_overlay(self, img):
        """
        Görüntüye ayarlanan metin, grafik ve şekil eklemelerini uygular
        
        Args:
            img: PIL Image nesnesi
            
        Returns:
            Eklemeler uygulanmış PIL Image nesnesi
        """
        if not self.text_enabled and not self.graphic_enabled and not self.shapes_enabled:
            return img
        
        # RGBA moduna dönüştür (şeffaflık için gerekli)
        result = img.convert("RGBA")
        
        # Şekil eklemelerini uygula
        if self.shapes_enabled and self.shapes:
            result = self._apply_shapes(result)
        
        # Grafik ekleme uygula
        if self.graphic_enabled and self.graphic_image:
            result = self._apply_graphic(result)
        
        # Metin ekleme uygula
        if self.text_enabled and self.text.strip():
            result = self._apply_text(result)
        
        # RGB moduna geri dönüştür (çıktı için)
        if result.mode == "RGBA":
            background = Image.new("RGB", result.size, (255, 255, 255))
            background.paste(result, mask=result.split()[3])  # Alpha kanalını maske olarak kullan
            return background
        else:
            return result

    def _apply_shapes(self, img):
        """
        Görüntüye şekiller ekler
        """
        width, height = img.size
        
        # Şekiller için yeni bir şeffaf katman oluştur
        shape_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shape_layer)
        
        # Her şekli çiz
        for shape in self.shapes:
            shape_type = shape.get('type', '')
            
            # Renk ve opaklık
            fill_color = shape.get('fill_color', None)
            outline_color = shape.get('outline_color', None)
            outline_width = shape.get('outline_width', 1)
            
            # Koordinatları görüntü boyutuna göre ölçeklendir
            if shape_type == 'rectangle':
                x1 = int(shape['x1'] * width)
                y1 = int(shape['y1'] * height)
                x2 = int(shape['x2'] * width)
                y2 = int(shape['y2'] * height)
                
                draw.rectangle(
                    [x1, y1, x2, y2],
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width
                )
                
            elif shape_type == 'ellipse':
                x1 = int(shape['x1'] * width)
                y1 = int(shape['y1'] * height)
                x2 = int(shape['x2'] * width)
                y2 = int(shape['y2'] * height)
                
                draw.ellipse(
                    [x1, y1, x2, y2],
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width
                )
                
            elif shape_type == 'line':
                x1 = int(shape['x1'] * width)
                y1 = int(shape['y1'] * height)
                x2 = int(shape['x2'] * width)
                y2 = int(shape['y2'] * height)
                
                draw.line(
                    [x1, y1, x2, y2],
                    fill=outline_color,
                    width=outline_width
                )
                
            elif shape_type == 'polygon':
                # Polygon için noktaları ölçeklendir
                points = []
                for point in shape['points']:
                    x = int(point[0] * width)
                    y = int(point[1] * height)
                    points.append((x, y))
                
                draw.polygon(
                    points,
                    fill=fill_color,
                    outline=outline_color
                )
                
            elif shape_type == 'parallelogram':
                # Paralelkenar için 4 nokta gerekli
                x = int(shape['x'] * width)  # sol üst köşe x
                y = int(shape['y'] * height)  # sol üst köşe y
                w = int(shape['w'] * width)   # genişlik
                h = int(shape['h'] * height)  # yükseklik
                skew = shape['skew']          # eğim faktörü
                
                # Paralelkenar köşe noktaları
                points = [
                    (x + skew, y),        # sol üst
                    (x + w + skew, y),    # sağ üst
                    (x + w, y + h),       # sağ alt
                    (x, y + h)            # sol alt
                ]
                
                draw.polygon(
                    points,
                    fill=fill_color,
                    outline=outline_color
                )
        
        # Şekil katmanını görüntüye ekle
        result = Image.alpha_composite(img, shape_layer)
        return result
    
    def _apply_text(self, img):
        """
        Görüntüye metin ekler
        """
        width, height = img.size
        
        # Metin boyutunu görüntü boyutuna göre ölçeklendir
        scaled_size = int(self.text_size * width / 1000)
        if scaled_size < 10:
            scaled_size = 10  # Minimum boyut
        
        font = self._get_font(scaled_size)
        
        # Metin için yeni bir şeffaf katman oluştur
        txt_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Metnin boyutlarını ölç - yeni PIL sürümüyle uyumlu
        try:
            # Pillow 9.0.0 ve üzeri için
            left, top, right, bottom = draw.textbbox((0, 0), self.text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:
            try:
                # Eski sürüm Pillow için
                text_width, text_height = draw.textsize(self.text, font=font)
            except AttributeError:
                # Varsayılan boyutlar
                text_width = len(self.text) * scaled_size // 2
                text_height = scaled_size + 4
        
        # Metin konumu
        if self.text_position_manual:
            # Özel konum kullan
            text_x = int(self.text_x_position * width) - (text_width // 2)
            text_y = int(self.text_y_position * height) - (text_height // 2)
        elif self.text_position == "bottom":
            text_x = (width - text_width) // 2
            text_y = height - text_height - 20  # alttan 20px boşluk
        elif self.text_position == "top":
            text_x = (width - text_width) // 2
            text_y = 20  # üstten 20px boşluk
        else:  # center
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2    
        
        # Metin opaklığı için alpha değerini hesapla
        alpha = int(255 * self.text_opacity / 100)
        
        # Eğer RGB tuple'ı 3 elemanlıysa alpha ekle, aksi takdirde mevcut alpha'yı güncelle
        if len(self.text_color) == 3:
            text_color = self.text_color + (alpha,)
        else:
            # Zaten 4 eleman varsa (RGBA), sadece alpha değerini güncelle
            text_color = self.text_color[:3] + (alpha,)
        
        # Dış çizgi varsa önce onu çiz
        if self.text_outline_width > 0:
            # Eğer RGB tuple'ı 3 elemanlıysa alpha ekle, aksi takdirde mevcut alpha'yı güncelle
            if len(self.text_outline_color) == 3:
                outline_color = self.text_outline_color + (alpha,)
            else:
                # Zaten 4 eleman varsa (RGBA), sadece alpha değerini güncelle
                outline_color = self.text_outline_color[:3] + (alpha,)
            
            # Çizgi kalınlığı için metni konumun etrafına çiz
            for offset_x in range(-self.text_outline_width, self.text_outline_width + 1):
                for offset_y in range(-self.text_outline_width, self.text_outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue  # Ana metni atla, bunu en son çizeceğiz
                    
                    # Çizgi kalınlığı 1 ise sadece ana yönleri çiz
                    if self.text_outline_width == 1:
                        if abs(offset_x) + abs(offset_y) != 1:
                            continue
                    
                    draw.text((text_x + offset_x, text_y + offset_y), self.text, 
                           font=font, fill=outline_color)
        
        # Ana metni çiz
        draw.text((text_x, text_y), self.text, font=font, fill=text_color)
        
        # Birleştirme işlemi
        result = Image.alpha_composite(img, txt_layer)
        return result
    
    def _apply_graphic(self, img):
        """
        Görüntüye grafik ekler
        """
        if not self.graphic_image:
            return img
        
        width, height = img.size
        
        # Grafik boyutunu hesapla (hedef görüntünün yüzdesi)
        target_width = int(width * self.graphic_size / 100)
        
        # Orijinal en-boy oranını koru
        graphic_width, graphic_height = self.graphic_image.size
        aspect_ratio = graphic_width / graphic_height
        target_height = int(target_width / aspect_ratio)
        
        # Grafiği yeniden boyutlandır
        resized_graphic = self.graphic_image.resize((target_width, target_height), Image.LANCZOS)
        
        # Opaklığı ayarla
        if self.graphic_opacity < 100:
            alpha_factor = self.graphic_opacity / 100
            resized_graphic = self._adjust_opacity(resized_graphic, alpha_factor)
        
        # Grafik konumu
        if self.graphic_position_manual:
            # Özel konum kullan
            graphic_x = int(self.graphic_x_position * width) - (target_width // 2)
            graphic_y = int(self.graphic_y_position * height) - (target_height // 2)
        elif self.graphic_position == "bottom-right":
            graphic_x = width - target_width - 20
            graphic_y = height - target_height - 20
        elif self.graphic_position == "bottom-left":
            graphic_x = 20
            graphic_y = height - target_height - 20
        elif self.graphic_position == "top-right":
            graphic_x = width - target_width - 20
            graphic_y = 20
        elif self.graphic_position == "top-left":
            graphic_x = 20
            graphic_y = 20
        else:  # center
            graphic_x = (width - target_width) // 2
            graphic_y = (height - target_height) // 2
        
        # Şeffaf bir katman oluştur ve grafiği yapıştır
        result = img.copy()
        result.paste(resized_graphic, (graphic_x, graphic_y), resized_graphic)
        
        return result
    
    def _adjust_opacity(self, img, alpha_factor):
        """
        Görüntü opaklığını ayarlar
        """
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        data = list(img.getdata())
        new_data = []
        
        for pixel in data:
            # Alfa kanalını (4. değer) ayarla
            r, g, b, a = pixel
            a = int(a * alpha_factor)
            new_data.append((r, g, b, a))
        
        img.putdata(new_data)
        return img